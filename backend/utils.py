"""Utility functions for TripVerse backend."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

logger = logging.getLogger(__name__)


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


def create_request_debug_dir(root_dir: str, request_prefix: str = "plan") -> tuple[str, str]:
    """Create a unique debug folder for a single planning request."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    request_id = f"{request_prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"
    debug_dir = Path(root_dir) / request_id
    debug_dir.mkdir(parents=True, exist_ok=True)
    return request_id, str(debug_dir)


def write_debug_text(debug_dir: str | None, filename: str, content: str) -> None:
    """Write text content to request debug folder without breaking request flow."""
    if not debug_dir:
        return
    try:
        path = Path(debug_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / filename).write_text(content or "", encoding="utf-8")
    except Exception as exc:
        logger.warning(f"Debug trace text write failed ({filename}): {exc}")


def write_debug_json(debug_dir: str | None, filename: str, payload: Any) -> None:
    """Write JSON content to request debug folder without breaking request flow."""
    if not debug_dir:
        return
    try:
        path = Path(debug_dir)
        path.mkdir(parents=True, exist_ok=True)
        with (path / filename).open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2, default=str)
    except Exception as exc:
        logger.warning(f"Debug trace json write failed ({filename}): {exc}")


def select_first_destination(destinations: Sequence[Any]):
    """Return the first destination from an ordered list, or None."""
    return destinations[0] if destinations else None


def dump_location_point(location: Any) -> Any:
    """Serialize a location point whether it is a pydantic model or plain dict."""
    if location is None:
        return None
    if hasattr(location, "model_dump"):
        return location.model_dump()
    return location


def dump_location_points(locations: Sequence[Any]) -> list[Any]:
    """Serialize a list of location points safely."""
    return [dump_location_point(location) for location in locations]
