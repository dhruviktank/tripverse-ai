"""Node for final plan aggregation."""

from __future__ import annotations

import json
from time import perf_counter

from orchestrator.state import TripPlanningState
from utils import dump_location_point, dump_location_points


async def run_finalize_plan(state: TripPlanningState, logger):
    """Finalize and persist complete plan in state."""
    node_started_at = perf_counter()
    itinerary_only = state.initial_draft or {}
    extras_only = state.food_budget_tips or {}
    combined_plan = state.refined_itinerary or {}

    final_plan = {
        "trip_description": state.trip_description,
        "source": dump_location_point(state.source),
        "destinations": dump_location_points(state.destinations),
        "budget": state.budget,
        "pace": state.pace,
        "itinerary": itinerary_only,
        "food_and_culture": extras_only.get("food_and_culture", []),
        "budget_breakdown": extras_only.get("budget_breakdown", []),
        "safety_and_practical_tips": extras_only.get("safety_and_practical_tips", []),
        "itinerary_only": itinerary_only,
        "food_budget_tips": extras_only,
        "combined": combined_plan,
        "context_sources": len(state.context_documents),
    }
    state.final_plan = final_plan
    logger.info(f"[TIMING] orchestrator.finalize_plan.total={perf_counter() - node_started_at:.3f}s")
    return {"final_plan": final_plan}
