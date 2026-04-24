"""Planning and discovery API routes."""

import json
import logging
from time import perf_counter

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from core.config import get_settings
from orchestrator.graph import get_trip_planning_orchestrator
from schemas.planning import HealthResponse, TripPlanRequest, TripPlanResponse
from services.location.service import get_location_service

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["Planning"])


def _build_trip_input(request: TripPlanRequest) -> dict:
    return {
        "trip_description": request.trip_description,
        "duration_days": request.duration_days,
        "preferences": request.preferences,
        "source": {"name": request.starting_from, "confidence": 1.0} if request.starting_from else None,
        "budget": request.budget,
        "pace": request.pace,
        "confirm_intent": request.confirm_intent,
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "version": settings.api_version}


@router.post("/api/trips/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripPlanRequest):
    request_started_at = perf_counter()
    try:
        orchestrator = get_trip_planning_orchestrator()
        trip_input = _build_trip_input(request)
        logger.info(f"Planning trip: {request.trip_description}")

        result = await orchestrator.plan_trip(trip_input)
        if result.get("success"):
            logger.info(f"[TIMING] plan_trip.total={perf_counter() - request_started_at:.3f}s")
            return TripPlanResponse(success=True, plan=result.get("plan"), errors=result.get("errors"))

        if result.get("validation") is not None:
            return TripPlanResponse(
                success=False,
                error=result.get("error"),
                errors=result.get("errors"),
                validation=result.get("validation"),
                requires_confirmation=bool(result.get("requires_confirmation", False)),
                requires_destination=bool(result.get("requires_destination", False)),
            )

        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate trip plan"))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error planning trip: {exc}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}")


@router.post("/api/trips/plan/stream")
async def plan_trip_stream(request: TripPlanRequest):
    orchestrator = get_trip_planning_orchestrator()
    trip_input = _build_trip_input(request)

    async def event_generator():
        async for event in orchestrator.plan_trip_stream(trip_input):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@router.get("/api/destinations/search")
async def search_destinations(query: str, limit: int = 5):
    try:
        location_service = get_location_service()
        results = await location_service.search_destinations(query=query, limit=limit)
        return {"query": query, "results": results, "count": len(results)}
    except Exception as exc:
        logger.error(f"Error searching destinations: {exc}")
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}")


@router.get("/", summary="Service info")
async def root():
    return {"message": "TripVerse AI Backend", "docs": "/docs", "version": settings.api_version}
