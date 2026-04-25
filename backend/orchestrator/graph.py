"""LangGraph orchestration graph and runtime facade."""

from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any, AsyncGenerator, Dict, Optional

from langgraph.graph import END, StateGraph

from core.config import get_settings
from llm.factory import get_llm_client
from orchestrator.nodes.finalize_plan import run_finalize_plan
from orchestrator.nodes.generate_plan import parse_json_response
from orchestrator.nodes.generate_plan import run_generate_plan
from orchestrator.nodes.retrieve_context import run_retrieve_context
from orchestrator.nodes.validate_request import run_validate_request
from orchestrator.prompts import EXTRAS_SYSTEM_PROMPT, ITINERARY_SYSTEM_PROMPT, TripPlanningInput, build_extras_prompt, build_itinerary_prompt
from orchestrator.state import TripPlanningState
from services.cache.service import get_cache_service
from services.retrieval.service import get_retrieval_service
from utils import (
    create_request_debug_dir,
    dump_location_point,
    dump_location_points,
    select_first_destination,
    write_debug_json,
    write_debug_text,
)

logger = logging.getLogger(__name__)


class TripPlanningOrchestrator:
    """Orchestrate trip planning using LangGraph."""

    def __init__(self):
        self.settings = get_settings()
        self.llm_client = get_llm_client()
        self.retrieval = get_retrieval_service()
        self.cache = get_cache_service()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(TripPlanningState)
        workflow.add_node("validate_request", self._validate_request)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_plan", self._generate_plan)
        workflow.add_node("finalize_plan", self._finalize_plan)

        workflow.set_entry_point("validate_request")
        workflow.add_conditional_edges(
            "validate_request",
            self._next_after_validation,
            {"proceed": "retrieve_context", "stop": END},
        )
        workflow.add_edge("retrieve_context", "generate_plan")
        workflow.add_edge("generate_plan", "finalize_plan")
        workflow.add_edge("finalize_plan", END)
        return workflow.compile()

    @staticmethod
    def _next_after_validation(state: TripPlanningState) -> str:
        return "proceed" if len(state.destinations) > 0 else "stop"

    async def _validate_request(self, state: TripPlanningState) -> Dict[str, Any]:
        return await run_validate_request(state, self.llm_client, logger)

    async def _retrieve_context(self, state: TripPlanningState) -> Dict[str, Any]:
        return await run_retrieve_context(state, self.retrieval, self.cache, logger)

    async def _generate_plan(self, state: TripPlanningState) -> Dict[str, Any]:
        return await run_generate_plan(state, self.llm_client, logger)

    async def _finalize_plan(self, state: TripPlanningState) -> Dict[str, Any]:
        return await run_finalize_plan(state, logger)

    async def plan_trip_stream(self, trip_input: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        flow_started_at = perf_counter()
        request_id, debug_trace_dir = create_request_debug_dir(self.settings.planning_debug_root, request_prefix="stream")
        # write_debug_json(debug_trace_dir, "00_request.json", {"request_id": request_id, "trip_input": trip_input})

        state = TripPlanningState(
            trip_description=trip_input.get("trip_description", ""),
            duration_days=int(trip_input.get("duration_days", 7) or 7),
            preferences=list(trip_input.get("preferences", []) or []),
            source=trip_input.get("source"),
            destinations=list(trip_input.get("destinations", []) or []),
            budget=trip_input.get("budget", ""),
            pace=trip_input.get("pace", ""),
            request_id=request_id,
            debug_trace_dir=debug_trace_dir,
            confirm_intent=bool(trip_input.get("confirm_intent", False)),
        )
        planning_input = TripPlanningInput(
            trip_description=state.trip_description,
            duration_days=state.duration_days,
            preferences=state.preferences,
            source=state.source,
            destinations=state.destinations,
            budget=state.budget,
            pace=state.pace,
        )

        try:
            validation_updates = await self._validate_request(state)
            for key, value in validation_updates.items():
                setattr(state, key, value)

            if not state.is_request_valid:
                validation_payload = state.validation or {}
                message = validation_payload.get("message") or "Invalid trip request"
                public_validation = {
                    "source": validation_payload.get("source"),
                    "destinations": validation_payload.get("destinations", []),
                }
                validation_event = {
                    "event": "validation",
                    "success": False,
                    "error": message,
                    "validation": public_validation,
                    "requires_confirmation": state.requires_confirmation,
                    "requires_destination": state.requires_destination,
                }
                # write_debug_json(debug_trace_dir, "99_final_result.json", validation_event)
                yield validation_event
                return

            await self._retrieve_context(state)

            context_snippets = []
            for doc in state.context_documents[:2]:
                metadata = doc.get("metadata") or {}
                snippet = (metadata.get("content") or "").strip()
                if snippet:
                    context_snippets.append(snippet[:500])
            context_block = "\n\n".join(context_snippets) if context_snippets else "No external context available."
            # write_debug_json(debug_trace_dir, "13_context_documents.json", state.context_documents[:2])
            # selected_destination = select_first_destination(state.destinations)

            itinerary_prompt = build_itinerary_prompt(planning_input, context_block)
            # write_debug_text(debug_trace_dir, "10_itinerary_prompt.txt", itinerary_prompt)
            itinerary_text = await self.llm_client.generate(
                prompt=itinerary_prompt,
                system_prompt=ITINERARY_SYSTEM_PROMPT,
            )
            # write_debug_text(debug_trace_dir, "11_itinerary_raw_response.txt", itinerary_text)
            itinerary_only = parse_json_response(itinerary_text)
            # write_debug_json(debug_trace_dir, "12_itinerary_parsed_response.json", itinerary_only)
            state.initial_draft = itinerary_only
            yield {
                "event": "itinerary",
                "success": True,
                "plan": {
                    "itinerary": itinerary_only,
                    "itinerary_only": itinerary_only,
                    "context_sources": len(state.context_documents),
                },
            }

            extras_prompt = build_extras_prompt(planning_input, context_block, itinerary_only)
            # write_debug_text(debug_trace_dir, "20_extras_prompt.txt", extras_prompt)
            extras_text = await self.llm_client.generate(
                prompt=extras_prompt,
                system_prompt=EXTRAS_SYSTEM_PROMPT,
            )
            # write_debug_text(debug_trace_dir, "21_extras_raw_response.txt", extras_text)
            extras_only = parse_json_response(extras_text)
            # write_debug_json(debug_trace_dir, "22_extras_parsed_response.json", extras_only)
            state.food_budget_tips = extras_only
            state.refined_itinerary = {
                "itinerary": itinerary_only,
                "food_and_culture": extras_only.get("food_and_culture", []),
                "budget_breakdown": extras_only.get("budget_breakdown", []),
                "safety_and_practical_tips": extras_only.get("safety_and_practical_tips", []),
            }
            yield {
                "event": "extras",
                "success": True,
                "plan": {
                    "food_budget_tips": extras_only,
                    "itinerary": state.refined_itinerary,
                },
            }

            result = await self._finalize_plan(state)
            # result = await self.graph.ainvoke(state.model_dump())
            # for key, value in result.items():
            #     if hasattr(state, key):
            #         setattr(state, key, value)
            # if not state.is_request_valid:
            #     validation_payload = state.validation or {}
            #     message = validation_payload.get("message") or "Invalid trip request"
            #     public_validation = {
            #         "source": validation_payload.get("source"),
            #         "destinations": validation_payload.get("destinations", []),
            #     }
            #     validation_event = {
            #         "event": "validation",
            #         "success": False,
            #         "error": message,
            #         "validation": public_validation,
            #         "requires_confirmation": state.requires_confirmation,
            #         "requires_destination": state.requires_destination,
            #     }
            #     # write_debug_json(debug_trace_dir, "99_final_result.json", validation_event)
            #     yield validation_event
            #     return
            # write_debug_json("debug_graph", "final_plan.json", result)
            logger.info(f"[TIMING] orchestrator.plan_trip_stream.total={perf_counter() - flow_started_at:.3f}s")
            yield {"event": "complete", "success": True, "plan": result.get("final_plan"), "errors": state.errors or None}
        except Exception as exc:
            logger.info(f"[TIMING] orchestrator.plan_trip_stream.total={perf_counter() - flow_started_at:.3f}s (exception)")
            print("Error:", exc)
            import traceback
            traceback.print_exc()
            state.errors.append(str(exc))
            error_event = {"event": "error", "success": False, "error": str(exc), "errors": state.errors}
            # write_debug_json(debug_trace_dir, "99_final_result.json", error_event)
            yield error_event

    async def plan_trip(self, trip_input: Dict[str, Any]) -> Dict[str, Any]:
        flow_started_at = perf_counter()
        request_id, debug_trace_dir = create_request_debug_dir(self.settings.planning_debug_root, request_prefix="plan")
        write_debug_json(debug_trace_dir, "00_request.json", {"request_id": request_id, "trip_input": trip_input})

        state = TripPlanningState(
            trip_description=trip_input.get("trip_description", ""),
            duration_days=int(trip_input.get("duration_days", 7) or 7),
            preferences=list(trip_input.get("preferences", []) or []),
            source=trip_input.get("source"),
            destinations=list(trip_input.get("destinations", []) or []),
            budget=trip_input.get("budget", ""),
            pace=trip_input.get("pace", ""),
            request_id=request_id,
            debug_trace_dir=debug_trace_dir,
            confirm_intent=bool(trip_input.get("confirm_intent", False)),
        )
        try:
            graph_started_at = perf_counter()
            result = await self.graph.ainvoke(state.model_dump())
            logger.info(f"[TIMING] orchestrator.graph_ainvoke={perf_counter() - graph_started_at:.3f}s")
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            elif not isinstance(result, dict):
                result = {"final_plan": result}

            if not result.get("is_request_valid", True):
                validation_payload = result.get("validation") or {}
                message = validation_payload.get("message") or "Invalid trip request"
                invalid_result = {
                    "success": False,
                    "error": message,
                    "errors": result.get("errors") or None,
                    "validation": validation_payload,
                    "requires_confirmation": bool(result.get("requires_confirmation", False)),
                    "requires_destination": bool(result.get("requires_destination", False)),
                }
                # write_debug_json(debug_trace_dir, "99_final_result.json", invalid_result)
                return invalid_result

            logger.info(f"[TIMING] orchestrator.plan_trip.total={perf_counter() - flow_started_at:.3f}s")
            success_result = {"success": True, "plan": result.get("final_plan"), "errors": result.get("errors") or None}
            # write_debug_json(debug_trace_dir, "99_final_result.json", success_result)
            return success_result
        except Exception as exc:
            logger.info(f"[TIMING] orchestrator.plan_trip.total={perf_counter() - flow_started_at:.3f}s (exception)")
            error_result = {"success": False, "error": str(exc), "errors": state.errors}
            # write_debug_json(debug_trace_dir, "99_final_result.json", error_result)
            return error_result


_orchestrator: Optional[TripPlanningOrchestrator] = None


def get_trip_planning_orchestrator() -> TripPlanningOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TripPlanningOrchestrator()
    return _orchestrator
