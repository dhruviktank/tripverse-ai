"""LLM-backed request validation before itinerary generation."""

from __future__ import annotations

import json
import re
from typing import Any

from llm.base import BaseLLMClient
from schemas.planning import LocationPoint, TripRequestValidation
from utils import write_debug_json, write_debug_text

VALIDATION_PROMPT_TEMPLATE = """You are a strict validator for a travel planning system.

Extract and classify the user input into JSON.

Return ONLY valid JSON:

{
  "is_valid_request": boolean,
  "travel_intent": boolean,
  "destinations": [{"name": string, "confidence": 0-1}],
  "preferences": [string],
  "missing_fields": [string],
  "message": string
}

Rules:
- Destination = real place (city/country/region), else []
- travel_intent = true ONLY if user wants to plan/visit/travel
- preferences = food, culture, nature, adventure, relax, nightlife, etc.
- is_valid_request = true ONLY at least one destination
- missing_fields: add "destination" or "intent" if missing
- If input is random/irrelevant → is_valid_request = false
- Do NOT hallucinate

Input:
"{user_input}"""


def _parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    return parsed if isinstance(parsed, dict) else {}


def _dedupe_locations(locations: list[LocationPoint]) -> list[LocationPoint]:
    seen: set[str] = set()
    deduped: list[LocationPoint] = []
    for location in locations:
        key = location.name.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(location)
    return deduped


def _to_validation_response(data: dict[str, Any]) -> TripRequestValidation:
    destinations_raw = data.get("destinations") if isinstance(data.get("destinations"), list) else []
    destinations: list[LocationPoint] = []
    for item in destinations_raw:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        try:
            confidence = float(item.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        destinations.append(LocationPoint(name=name, confidence=confidence))

    destinations = _dedupe_locations(destinations)

    source_raw = data.get("source") if isinstance(data.get("source"), dict) else None
    source: LocationPoint | None = None
    if source_raw:
        source_name = str(source_raw.get("name", "")).strip()
        if source_name:
            try:
                source_confidence = float(source_raw.get("confidence", 1.0))
            except (TypeError, ValueError):
                source_confidence = 1.0
            source = LocationPoint(name=source_name, confidence=max(0.0, min(1.0, source_confidence)))

    preferences_raw = data.get("preferences") if isinstance(data.get("preferences"), list) else []
    preferences = [str(item).strip() for item in preferences_raw if str(item).strip()]

    missing_raw = data.get("missing_fields") if isinstance(data.get("missing_fields"), list) else []
    missing_fields = [str(item).strip().lower() for item in missing_raw if str(item).strip()]

    message = str(data.get("message") or "Please provide a clear travel request with destination and intent.").strip()

    return TripRequestValidation(
        source=source,
        destinations=destinations,
        is_valid_request=bool(data.get("is_valid_request", False)),
        travel_intent=bool(data.get("travel_intent", False)),
        preferences=preferences,
        missing_fields=missing_fields,
        message=message,
    )


async def validate_trip_request(
    llm_client: BaseLLMClient,
    user_input: str,
    source_name: str | None = None,
    debug_trace_dir: str | None = None,
) -> TripRequestValidation:
    prompt = VALIDATION_PROMPT_TEMPLATE.replace("{user_input}", user_input)
    write_debug_text(debug_trace_dir, "01_validation_prompt.txt", prompt)
    try:
        raw = await llm_client.generate(prompt=prompt)
        write_debug_text(debug_trace_dir, "02_validation_raw_response.txt", raw)
        parsed = _parse_json_response(raw)
        if source_name:
            parsed["source"] = {"name": source_name, "confidence": 1.0}
        write_debug_json(debug_trace_dir, "03_validation_parsed_response.json", parsed)
        validation_result = _to_validation_response(parsed)
        write_debug_json(debug_trace_dir, "04_validation_result.json", validation_result.model_dump())
        return validation_result
    except Exception:
        fallback = {
            "source": {"name": source_name, "confidence": 1.0} if source_name else None,
            "is_valid_request": False,
            "travel_intent": False,
            "destinations": [],
            "preferences": [],
            "missing_fields": ["intent", "destination"],
            "message": "I could not validate your request. Please share your travel intent and destination.",
        }
        write_debug_json(debug_trace_dir, "04_validation_fallback.json", fallback)
        return _to_validation_response(fallback)
