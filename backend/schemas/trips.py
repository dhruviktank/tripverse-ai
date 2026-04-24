"""Trip CRUD API schemas."""

from typing import Optional

from pydantic import BaseModel, Field


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
