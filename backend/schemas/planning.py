"""Trip planning API schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    """Request model for trip planning."""

    trip_description: str = Field(..., description="Description of the desired trip")
    duration_days: int = Field(7, ge=1, le=30, description="Trip duration in days")
    preferences: list[str] = Field(default_factory=list, description="Traveler preferences")
    budget: str = Field(..., description="Budget range (e.g., 'Value explorer', 'Balanced')")
    pace: str = Field(..., description="Travel pace (e.g., 'Relaxed', 'Balanced', 'High energy')")
    starting_from: str = Field(..., description="Starting location for the trip")
    confirm_intent: bool = Field(False, description="User-confirmed intent when validator flags missing intent")


class LocationPoint(BaseModel):
    """Named location with confidence."""

    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class TripLocationSelection(BaseModel):
    """Public validation output exposing source and ordered destinations only."""

    source: Optional[LocationPoint] = None
    destinations: list[LocationPoint] = Field(default_factory=list)


class TripRequestValidation(TripLocationSelection):
    """Structured request validation output produced by the LLM validator."""

    is_valid_request: bool
    travel_intent: bool
    preferences: list[str]
    missing_fields: list[str]
    message: str


class TripPlanResponse(BaseModel):
    """Response model for trip planning."""

    success: bool
    plan: Optional[dict] = None
    error: Optional[str] = None
    errors: Optional[list] = None
    validation: Optional[TripLocationSelection] = None
    requires_confirmation: bool = False
    requires_destination: bool = False


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
