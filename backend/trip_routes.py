"""Trip CRUD API routes: save, list, get, update, delete, favorite, regenerate, dashboard stats."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db
from models import User, Trip
from auth import get_current_user
from orchestrator import get_trip_planning_orchestrator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trips", tags=["Trips"])


# --- Request / Response schemas ---

class SaveTripRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    trip_description: str = Field(..., min_length=1)
    budget: str = Field(..., min_length=1, max_length=50)
    pace: str = Field(..., min_length=1, max_length=50)
    starting_from: str = Field(..., min_length=1, max_length=255)
    preferences: Optional[str] = None
    itinerary_data: Optional[dict] = None
    itinerary_text: Optional[str] = None
    budget_spent: Optional[float] = None
    budget_total: Optional[float] = None
    travelers: int = 1
    dates: Optional[str] = None
    status: str = "upcoming"


class UpdateTripRequest(BaseModel):
    title: Optional[str] = None
    trip_description: Optional[str] = None
    status: Optional[str] = None
    itinerary_data: Optional[dict] = None
    itinerary_text: Optional[str] = None
    budget_spent: Optional[float] = None
    budget_total: Optional[float] = None
    travelers: Optional[int] = None
    dates: Optional[str] = None
    preferences: Optional[str] = None


class TripResponse(BaseModel):
    success: bool
    trip: Optional[dict] = None
    message: Optional[str] = None


class TripListResponse(BaseModel):
    success: bool
    trips: list[dict]
    total: int
    message: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    success: bool
    stats: dict


# --- Routes ---

@router.post("/save", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def save_trip(
    request: SaveTripRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a new trip for the authenticated user."""
    trip = Trip(
        user_id=current_user.id,
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
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    logger.info(f"Trip saved: {trip.title} by user {current_user.email}")
    return TripResponse(
        success=True,
        trip=trip.to_dict(),
        message="Trip saved successfully",
    )


@router.get("", response_model=TripListResponse)
async def list_trips(
    filter: Optional[str] = Query(None, description="Filter: all, upcoming, past, favorites"),
    sort_by: Optional[str] = Query("newest", description="Sort: newest, oldest, budget_high, budget_low, duration"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all trips for the authenticated user with optional filter and sort."""
    query = select(Trip).where(Trip.user_id == current_user.id)

    # Apply filter
    if filter == "upcoming":
        query = query.where(Trip.status == "upcoming")
    elif filter == "past":
        query = query.where(Trip.status == "past")
    elif filter == "favorites":
        query = query.where(Trip.is_favorite == True)

    # Apply sort
    if sort_by == "newest":
        query = query.order_by(desc(Trip.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Trip.created_at))
    elif sort_by == "budget_high":
        query = query.order_by(desc(Trip.budget_total))
    elif sort_by == "budget_low":
        query = query.order_by(asc(Trip.budget_total))
    else:
        query = query.order_by(desc(Trip.created_at))

    result = await db.execute(query)
    trips = result.scalars().all()

    return TripListResponse(
        success=True,
        trips=[t.to_dict() for t in trips],
        total=len(trips),
    )


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single trip by ID (must belong to current user)."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return TripResponse(success=True, trip=trip.to_dict())


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    request: UpdateTripRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a trip (notes, itinerary data, status, etc.)."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    # Update only provided fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)

    await db.commit()
    await db.refresh(trip)

    logger.info(f"Trip updated: {trip.title}")
    return TripResponse(
        success=True,
        trip=trip.to_dict(),
        message="Trip updated successfully",
    )


@router.delete("/{trip_id}", status_code=status.HTTP_200_OK)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

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
    """Toggle the favorite status of a trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    trip.is_favorite = not trip.is_favorite
    await db.commit()
    await db.refresh(trip)

    status_text = "added to" if trip.is_favorite else "removed from"
    logger.info(f"Trip {trip_id} {status_text} favorites")
    return TripResponse(
        success=True,
        trip=trip.to_dict(),
        message=f"Trip {status_text} favorites",
    )


@router.post("/{trip_id}/duplicate", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate an existing trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    new_trip = Trip(
        user_id=current_user.id,
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
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)

    logger.info(f"Trip duplicated: {original.title} → {new_trip.title}")
    return TripResponse(
        success=True,
        trip=new_trip.to_dict(),
        message="Trip duplicated successfully",
    )


@router.post("/{trip_id}/regenerate", response_model=TripResponse)
async def regenerate_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate the itinerary for an existing trip using the original parameters."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    try:
        orchestrator = get_trip_planning_orchestrator()
        trip_input = {
            "trip_description": trip.trip_description,
            "budget": trip.budget,
            "pace": trip.pace,
            "starting_from": trip.starting_from,
        }

        logger.info(f"Regenerating trip: {trip.title}")
        plan_result = await orchestrator.plan_trip(trip_input)

        if plan_result.get("success"):
            plan = plan_result.get("plan", {})
            trip.itinerary_text = plan.get("itinerary", trip.itinerary_text)
            await db.commit()
            await db.refresh(trip)

            return TripResponse(
                success=True,
                trip=trip.to_dict(),
                message="Itinerary regenerated successfully",
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=plan_result.get("error", "Failed to regenerate itinerary"),
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating trip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")


# --- Dashboard Stats (separate router) ---

dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@dashboard_router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the authenticated user."""
    # Total trips
    total_result = await db.execute(
        select(func.count(Trip.id)).where(Trip.user_id == current_user.id)
    )
    total_trips = total_result.scalar() or 0

    # Upcoming trips count
    upcoming_result = await db.execute(
        select(func.count(Trip.id)).where(
            Trip.user_id == current_user.id, Trip.status == "upcoming"
        )
    )
    upcoming_trips = upcoming_result.scalar() or 0

    # Average budget
    avg_budget_result = await db.execute(
        select(func.avg(Trip.budget_total)).where(
            Trip.user_id == current_user.id, Trip.budget_total.isnot(None)
        )
    )
    avg_budget = avg_budget_result.scalar() or 0

    # Recent trips (last 4)
    recent_result = await db.execute(
        select(Trip)
        .where(Trip.user_id == current_user.id)
        .order_by(desc(Trip.created_at))
        .limit(4)
    )
    recent_trips = recent_result.scalars().all()

    # Next upcoming trip
    next_trip_result = await db.execute(
        select(Trip)
        .where(Trip.user_id == current_user.id, Trip.status == "upcoming")
        .order_by(asc(Trip.created_at))
        .limit(1)
    )
    next_trip = next_trip_result.scalar_one_or_none()

    return DashboardStatsResponse(
        success=True,
        stats={
            "total_trips": total_trips,
            "upcoming_trips": upcoming_trips,
            "average_budget": round(float(avg_budget), 2),
            "recent_trips": [t.to_dict() for t in recent_trips],
            "next_trip": next_trip.to_dict() if next_trip else None,
        },
    )
