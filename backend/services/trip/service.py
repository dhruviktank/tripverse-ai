"""Trip query, mutation, and aggregation service."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Trip
from schemas.trips import SaveTripRequest, UpdateTripRequest


def build_trip_list_query(user_id: str, filter_name: Optional[str] = None, sort_by: str = "newest"):
    query = select(Trip).where(Trip.user_id == user_id)
    if filter_name == "upcoming":
        query = query.where(Trip.status == "upcoming")
    elif filter_name == "past":
        query = query.where(Trip.status == "past")
    elif filter_name == "favorites":
        query = query.where(Trip.is_favorite.is_(True))

    if sort_by == "newest":
        return query.order_by(desc(Trip.created_at))
    if sort_by == "oldest":
        return query.order_by(asc(Trip.created_at))
    if sort_by == "budget_high":
        return query.order_by(desc(Trip.budget_total))
    if sort_by == "budget_low":
        return query.order_by(asc(Trip.budget_total))
    return query.order_by(desc(Trip.created_at))


async def get_trip_for_user(db: AsyncSession, trip_id: str, user_id: str) -> Trip:
    result = await db.execute(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


async def list_user_trips(
    db: AsyncSession,
    user_id: str,
    filter_name: Optional[str] = None,
    sort_by: str = "newest",
) -> list[Trip]:
    result = await db.execute(build_trip_list_query(user_id, filter_name, sort_by))
    return list(result.scalars().all())


def clone_trip(original: Trip, user_id: str) -> Trip:
    return Trip(
        user_id=user_id,
        title=f"{original.title} (Copy)",
        trip_description=original.trip_description,
        budget=original.budget,
        pace=original.pace,
        starting_from=original.starting_from,
        preferences=original.preferences,
        itinerary_data=original.itinerary_data,
        itinerary_text=original.itinerary_text,
        budget_spent=original.budget_spent,
        budget_total=original.budget_total,
        travelers=original.travelers,
        dates=original.dates,
        status="draft",
    )


def build_trip_input(trip: Trip) -> dict:
    return {
        "trip_description": trip.trip_description,
        "budget": trip.budget,
        "pace": trip.pace,
        "source": {"name": trip.starting_from, "confidence": 1.0} if trip.starting_from else None,
    }


def create_trip_from_request(user_id: str, request: SaveTripRequest) -> Trip:
    return Trip(
        user_id=user_id,
        title=request.title,
        trip_description=request.trip_description,
        budget=request.budget,
        pace=request.pace,
        starting_from=request.starting_from,
        preferences=request.preferences,
        itinerary_data=request.itinerary_data,
        itinerary_text=request.itinerary_text,
        budget_spent=request.budget_spent,
        budget_total=request.budget_total,
        travelers=request.travelers,
        dates=request.dates,
        status=request.status,
    )


def apply_trip_updates(trip: Trip, request: UpdateTripRequest) -> Trip:
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
    return trip


def serialize_plan(plan: dict) -> str:
    return json.dumps(plan, ensure_ascii=False)


async def persist_plan(trip: Trip, plan: dict, db: AsyncSession) -> Trip:
    trip.itinerary_data = plan
    trip.itinerary_text = serialize_plan(plan)
    await db.commit()
    await db.refresh(trip)
    return trip


async def build_dashboard_stats(db: AsyncSession, user_id: str) -> dict:
    total_result = await db.execute(select(func.count(Trip.id)).where(Trip.user_id == user_id))
    upcoming_result = await db.execute(
        select(func.count(Trip.id)).where(Trip.user_id == user_id, Trip.status == "upcoming")
    )
    avg_budget_result = await db.execute(
        select(func.avg(Trip.budget_total)).where(Trip.user_id == user_id, Trip.budget_total.isnot(None))
    )
    recent_result = await db.execute(
        select(Trip).where(Trip.user_id == user_id).order_by(desc(Trip.created_at)).limit(4)
    )
    next_trip_result = await db.execute(
        select(Trip).where(Trip.user_id == user_id, Trip.status == "upcoming").order_by(asc(Trip.created_at)).limit(1)
    )

    total_trips = total_result.scalar() or 0
    upcoming_trips = upcoming_result.scalar() or 0
    avg_budget = avg_budget_result.scalar() or 0
    recent_trips = recent_result.scalars().all()
    next_trip = next_trip_result.scalar_one_or_none()

    return {
        "total_trips": total_trips,
        "upcoming_trips": upcoming_trips,
        "average_budget": round(float(avg_budget), 2),
        "recent_trips": [trip.to_dict() for trip in recent_trips],
        "next_trip": next_trip.to_dict() if next_trip else None,
    }
