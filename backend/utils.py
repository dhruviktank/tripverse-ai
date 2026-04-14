"""Utility functions for TripVerse backend."""

from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


def parse_budget_range(budget_str: str) -> Dict[str, int]:
    """
    Parse budget string into min/max values in USD.
    
    Args:
        budget_str: Budget category (e.g., "Value explorer", "Balanced", "Luxury moments")
    
    Returns:
        Dictionary with min and max budget values
    """
    budget_ranges = {
        "value_explorer": {"min": 500, "max": 1500},
        "balanced": {"min": 1500, "max": 3500},
        "luxury_moments": {"min": 3500, "max": 10000},
    }
    
    key = budget_str.lower().replace(" ", "_")
    return budget_ranges.get(key, budget_ranges["balanced"])


def parse_pace(pace_str: str) -> Dict[str, Any]:
    """
    Parse pace preference into activity level.
    
    Args:
        pace_str: Pace type (e.g., "Relaxed", "Balanced", "High energy")
    
    Returns:
        Dictionary with pace metadata
    """
    paces = {
        "relaxed": {
            "activities_per_day": 2,
            "avg_daily_hours": 4,
            "rest_days_per_week": 2
        },
        "balanced": {
            "activities_per_day": 4,
            "avg_daily_hours": 7,
            "rest_days_per_week": 1
        },
        "high_energy": {
            "activities_per_day": 6,
            "avg_daily_hours": 10,
            "rest_days_per_week": 0
        },
    }
    
    key = pace_str.lower()
    return paces.get(key, paces["balanced"])


def validate_trip_request(request_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate trip planning request data.
    
    Args:
        request_data: Trip request data
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["trip_description", "budget", "pace", "starting_from"]
    
    for field in required_fields:
        if field not in request_data or not request_data[field].strip():
            return False, f"Missing required field: {field}"
    
    if len(request_data["trip_description"]) < 10:
        return False, "Trip description too short (minimum 10 characters)"
    
    valid_budgets = ["value_explorer", "balanced", "luxury_moments"]
    if request_data["budget"].lower().replace(" ", "_") not in valid_budgets:
        return False, "Invalid budget category"
    
    valid_paces = ["relaxed", "balanced", "high_energy"]
    if request_data["pace"].lower() not in valid_paces:
        return False, "Invalid pace type"
    
    return True, ""


def format_itinerary(itinerary_data: str) -> Dict[str, Any]:
    """
    Format raw itinerary data into structured format.
    
    Args:
        itinerary_data: Raw itinerary text
    
    Returns:
        Structured itinerary dictionary
    """
    try:
        # Try to parse as JSON first
        return json.loads(itinerary_data)
    except json.JSONDecodeError:
        # Fallback to text format
        return {
            "raw_itinerary": itinerary_data,
            "format": "text"
        }


def calculate_trip_duration(trip_description: str) -> int:
    """
    Extract trip duration from description.
    
    Args:
        trip_description: Trip description text
    
    Returns:
        Estimated duration in days
    """
    import re
    
    # Look for patterns like "7 days", "10-day", "2 weeks"
    days_match = re.search(r'(\d+)\s*(?:day|days|d)', trip_description, re.IGNORECASE)
    if days_match:
        return int(days_match.group(1))
    
    weeks_match = re.search(r'(\d+)\s*(?:week|weeks|w)', trip_description, re.IGNORECASE)
    if weeks_match:
        return int(weeks_match.group(1)) * 7
    
    # Default to 7 days if not specified
    return 7


def extract_destinations(trip_description: str) -> List[str]:
    """
    Extract mentioned destinations from trip description.
    
    Args:
        trip_description: Trip description text
    
    Returns:
        List of destination names
    """
    # This is a simplified extraction - in production, use NLP
    import re
    
    # Common location keywords
    prepositions = ["in", "to", "around", "through", "via"]
    pattern = r'(?:' + '|'.join(prepositions) + r')\s+([A-Z][a-zA-Z\s]+)'
    
    matches = re.findall(pattern, trip_description)
    return [match.strip() for match in matches]


def create_budget_breakdown(budget_str: str, duration_days: int) -> Dict[str, float]:
    """
    Create a budget breakdown by category.
    
    Args:
        budget_str: Budget category
        duration_days: Trip duration in days
    
    Returns:
        Budget breakdown by category
    """
    total_budget = parse_budget_range(budget_str)["max"]
    daily_budget = total_budget / duration_days
    
    breakdown = {
        "accommodation": daily_budget * 0.35,
        "food": daily_budget * 0.30,
        "activities": daily_budget * 0.20,
        "transportation": daily_budget * 0.10,
        "miscellaneous": daily_budget * 0.05,
    }
    
    return {k: round(v, 2) for k, v in breakdown.items()}


def log_trip_planning(request_data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """
    Log trip planning for analytics.
    
    Args:
        request_data: Original request data
        result: Result from trip planning
    """
    log_entry = {
        "action": "trip_planned",
        "trip_description": request_data.get("trip_description", "")[:50],
        "budget": request_data.get("budget"),
        "pace": request_data.get("pace"),
        "starting_from": request_data.get("starting_from"),
        "success": result.get("success", False),
        "errors": result.get("errors", [])
    }
    logger.info(f"Trip Planning: {json.dumps(log_entry)}")
