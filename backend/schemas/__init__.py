"""Pydantic schemas used by the TripVerse backend."""

from .auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from .planning import HealthResponse, TripPlanRequest, TripPlanResponse
from .trips import (
    DashboardStatsResponse,
    SaveTripRequest,
    TripListResponse,
    TripResponse,
    UpdateTripRequest,
)
