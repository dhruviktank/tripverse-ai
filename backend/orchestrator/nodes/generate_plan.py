"""Node for generating itinerary and supporting sections."""

from __future__ import annotations

import json
from time import perf_counter

from orchestrator.prompts import (
    EXTRAS_SYSTEM_PROMPT,
    ITINERARY_SYSTEM_PROMPT,
    TripPlanningInput,
    build_extras_prompt,
    build_itinerary_prompt,
)
from orchestrator.state import TripPlanningState
from utils import write_debug_json, write_debug_text


def parse_json_response(response_text: str) -> dict:
    """Parse JSON from model response text, including wrapped payloads."""
    import re

    cleaned = response_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))

    if isinstance(parsed, list):
        return {"items": parsed}
    if not isinstance(parsed, dict):
        return {"value": parsed}
    return parsed

async def run_generate_plan(state: TripPlanningState, llm_client, logger):
    """Generate itinerary and extras using two model calls."""
    node_started_at = perf_counter()
    planning_input = TripPlanningInput(
        duration_days=state.duration_days,
        preferences=state.preferences,
        trip_description=state.trip_description,
        budget=state.budget,
        pace=state.pace,
        source=state.source,
        destinations=state.destinations,
    )

    prompt_started_at = perf_counter()
    context_snippets = []
    for doc in state.context_documents[:2]:
        metadata = doc.get("metadata") or {}
        snippet = (metadata.get("content") or "").strip()
        if snippet:
            context_snippets.append(snippet[:500])
    context_block = "\n\n".join(context_snippets) if context_snippets else "No external context available."
    # write_debug_json(state.debug_trace_dir, "13_context_documents.json", state.context_documents[:2])
    # write_debug_text(state.debug_trace_dir, "14_context_block.txt", context_block)
    itinerary_user_prompt = build_itinerary_prompt(planning_input, context_block)
    # write_debug_text(state.debug_trace_dir, "10_itinerary_prompt.txt", itinerary_user_prompt)
    logger.info(f"[TIMING] orchestrator.generate_plan.build_prompt={perf_counter() - prompt_started_at:.3f}s")

    try:
        itinerary_started_at = perf_counter()
        itinerary_text = await llm_client.generate(prompt=itinerary_user_prompt, system_prompt=ITINERARY_SYSTEM_PROMPT)
        # write_debug_text(state.debug_trace_dir, "11_itinerary_raw_response.txt", itinerary_text)
        logger.info(
            f"[TIMING] orchestrator.generate_plan.llm_generate_itinerary={perf_counter() - itinerary_started_at:.3f}s"
        )
        itinerary_data = parse_json_response(itinerary_text)
        # write_debug_json(state.debug_trace_dir, "12_itinerary_parsed_response.json", itinerary_data)

        extras_prompt_started_at = perf_counter()
        extras_user_prompt = build_extras_prompt(planning_input, context_block, itinerary_data)
        # write_debug_text(state.debug_trace_dir, "20_extras_prompt.txt", extras_user_prompt)
        logger.info(
            f"[TIMING] orchestrator.generate_plan.build_extras_prompt={perf_counter() - extras_prompt_started_at:.3f}s"
        )

        extras_started_at = perf_counter()
        extras_text = await llm_client.generate(prompt=extras_user_prompt, system_prompt=EXTRAS_SYSTEM_PROMPT)
        # write_debug_text(state.debug_trace_dir, "21_extras_raw_response.txt", extras_text)
        logger.info(
            f"[TIMING] orchestrator.generate_plan.llm_generate_extras={perf_counter() - extras_started_at:.3f}s"
        )
        extras_data = parse_json_response(extras_text)
        # write_debug_json(state.debug_trace_dir, "22_extras_parsed_response.json", extras_data)

        state.initial_draft = itinerary_data
        state.refined_itinerary = {
            "itinerary": itinerary_data,
            "food_and_culture": extras_data.get("food_and_culture", []),
            "budget_breakdown": extras_data.get("budget_breakdown", []),
            "safety_and_practical_tips": extras_data.get("safety_and_practical_tips", []),
        }
        state.food_budget_tips = extras_data
        logger.info(f"[TIMING] orchestrator.generate_plan.total={perf_counter() - node_started_at:.3f}s")
        return {
            "initial_draft": itinerary_data,
            "refined_itinerary": state.refined_itinerary,
            "food_budget_tips": extras_data,
        }
    except Exception as exc:
        state.errors.append(f"Plan generation error: {exc}")
        logger.info(f"[TIMING] orchestrator.generate_plan.total={perf_counter() - node_started_at:.3f}s (exception)")
        return {}
