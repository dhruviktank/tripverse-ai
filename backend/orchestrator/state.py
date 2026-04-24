"""State definitions for trip planning orchestration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.planning import LocationPoint


class TripPlanningState(BaseModel):
    """State for trip planning workflow."""

    trip_description: str
    duration_days: int = 7
    preferences: List[str] = Field(default_factory=list)
    source: Optional[LocationPoint] = None
    destinations: List[LocationPoint] = Field(default_factory=list)
    budget: str
    pace: str
    request_id: Optional[str] = None
    debug_trace_dir: Optional[str] = None
    confirm_intent: bool = False
    is_request_valid: bool = True
    requires_confirmation: bool = False
    requires_destination: bool = False
    validation: Optional[Dict[str, Any]] = None
    context_documents: List[Dict[str, Any]] = Field(default_factory=list)
    initial_draft: Optional[Dict[str, Any]] = None
    refined_itinerary: Optional[Dict[str, Any]] = None
    food_budget_tips: Optional[Dict[str, Any]] = None
    final_plan: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
