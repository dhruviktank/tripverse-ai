"""Trip CRUD API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_db
from models import User
from orchestrator.graph import get_trip_planning_orchestrator
from schemas.trips import SaveTripRequest, TripListResponse, TripResponse, UpdateTripRequest
from services.trip.service import (
    apply_trip_updates,
    build_trip_input,
    clone_trip,
    create_trip_from_request,
    get_trip_for_user,
    list_user_trips,
    persist_plan,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.post("/save", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def save_trip(
    request: SaveTripRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = create_trip_from_request(current_user.id, request)
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    logger.info(f"Trip saved: {trip.title} by user {current_user.email}")
    return TripResponse(success=True, trip=trip.to_dict(), message="Trip saved successfully")


@router.get("", response_model=TripListResponse)
async def list_trips(
    filter: str | None = Query(None, description="Filter: all, upcoming, past, favorites"),
    sort_by: str | None = Query("newest", description="Sort: newest, oldest, budget_high, budget_low, duration"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trips = await list_user_trips(db, current_user.id, filter, sort_by or "newest")
    return TripListResponse(success=True, trips=[t.to_dict() for t in trips], total=len(trips))


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await get_trip_for_user(db, trip_id, current_user.id)
    return TripResponse(success=True, trip=trip.to_dict())


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    request: UpdateTripRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await get_trip_for_user(db, trip_id, current_user.id)
    apply_trip_updates(trip, request)
    await db.commit()
    await db.refresh(trip)
    logger.info(f"Trip updated: {trip.title}")
    return TripResponse(success=True, trip=trip.to_dict(), message="Trip updated successfully")


@router.delete("/{trip_id}", status_code=status.HTTP_200_OK)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await get_trip_for_user(db, trip_id, current_user.id)
    await db.delete(trip)
    await db.commit()
    logger.info(f"Trip deleted: {trip_id} by user {current_user.email}")
    return {"success": True, "message": "Trip deleted successfully"}


@router.patch("/{trip_id}/favorite", response_model=TripResponse)
async def toggle_favorite(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await get_trip_for_user(db, trip_id, current_user.id)
    trip.is_favorite = not trip.is_favorite
    await db.commit()
    await db.refresh(trip)

    status_text = "added to" if trip.is_favorite else "removed from"
    logger.info(f"Trip {trip_id} {status_text} favorites")
    return TripResponse(success=True, trip=trip.to_dict(), message=f"Trip {status_text} favorites")


@router.post("/{trip_id}/duplicate", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    original = await get_trip_for_user(db, trip_id, current_user.id)
    new_trip = clone_trip(original, current_user.id)
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)
    logger.info(f"Trip duplicated: {original.title} -> {new_trip.title}")
    return TripResponse(success=True, trip=new_trip.to_dict(), message="Trip duplicated successfully")


@router.post("/{trip_id}/regenerate", response_model=TripResponse)
async def regenerate_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await get_trip_for_user(db, trip_id, current_user.id)

    try:
        orchestrator = get_trip_planning_orchestrator()
        trip_input = build_trip_input(trip)
        logger.info(f"Regenerating trip: {trip.title}")
        plan_result = await orchestrator.plan_trip(trip_input)

        if plan_result.get("success"):
            plan = plan_result.get("plan", {})
            await persist_plan(trip, plan, db)
            return TripResponse(success=True, trip=trip.to_dict(), message="Itinerary regenerated successfully")

        raise HTTPException(status_code=500, detail=plan_result.get("error", "Failed to regenerate itinerary"))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error regenerating trip: {exc}")
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {exc}")
