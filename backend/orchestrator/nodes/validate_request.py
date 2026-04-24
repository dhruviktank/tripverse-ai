"""Node for validating user trip intent before planning."""

from __future__ import annotations

from time import perf_counter

from orchestrator.state import TripPlanningState
from services.trip.validation import validate_trip_request


async def run_validate_request(state: TripPlanningState, llm_client, logger):
    node_started_at = perf_counter()
    validation = await validate_trip_request(
        llm_client,
        state.trip_description,
        source_name=state.source.name if state.source else None,
        debug_trace_dir=state.debug_trace_dir,
    )
    missing_fields = set(validation.missing_fields)
    has_destination = len(validation.destinations) > 0

    is_valid = validation.is_valid_request
    requires_confirmation = False
    requires_destination = False

    if not is_valid:
        only_destination_without_intent = has_destination and ("intent" in missing_fields or not validation.travel_intent)
        only_intent_without_destination = validation.travel_intent and (
            "destination" in missing_fields or not has_destination
        )

        if only_destination_without_intent:
            if state.confirm_intent:
                is_valid = True
            else:
                requires_confirmation = True
        elif only_intent_without_destination:
            requires_destination = True
        elif "destination" in missing_fields:
            requires_destination = True

    logger.info(f"[TIMING] orchestrator.validate_request.total={perf_counter() - node_started_at:.3f}s")
    return {
        "validation": validation.model_dump(),
        "source": validation.source if validation.source else state.source,
        "destinations": validation.destinations,
        "is_request_valid": is_valid,
        "requires_confirmation": requires_confirmation,
        "requires_destination": requires_destination,
    }
