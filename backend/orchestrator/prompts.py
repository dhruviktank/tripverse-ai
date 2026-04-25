"""Prompt builders used by orchestrator nodes."""

from __future__ import annotations

from dataclasses import dataclass

from schemas.planning import LocationPoint
from utils import calculate_trip_duration, select_first_destination


@dataclass(frozen=True)
class TripPlanningInput:
    trip_description: str
    duration_days: int
    preferences: list[str] | None
    source: LocationPoint | None
    destinations: list[LocationPoint] | None
    budget: str
    pace: str


ITINERARY_SYSTEM_PROMPT = """You are a senior travel planning assistant.
Your job is to produce practical, realistic, and user-ready trip outputs.

Response policy:
- Return only valid JSON matching the requested schema.
- Do not include markdown, code fences, explanations, or reasoning.
- Keep recommendations feasible for the stated budget, pace, and duration.
- Prefer concrete, actionable details over generic statements."""


EXTRAS_SYSTEM_PROMPT = """You are a senior travel planning assistant.
Produce concise but useful support sections that align with the itinerary.

Response policy:
- Return only valid JSON matching the requested schema.
- Do not include markdown, code fences, explanations, or reasoning.
- Keep budget estimates realistic and internally consistent.
- Keep safety/practical guidance specific to destination conditions."""


def build_itinerary_prompt(planning_input: TripPlanningInput, context_block: str) -> str:
    duration_days = planning_input.duration_days or calculate_trip_duration(planning_input.trip_description)
    preferences_text = ", ".join(planning_input.preferences) if planning_input.preferences else "No explicit preferences provided"
    source_text = planning_input.source.name if planning_input.source else "Unknown"
    destination_names = [destination.name for destination in planning_input.destinations]
    selected_destination = select_first_destination(planning_input.destinations)
    destination_text = ", ".join(destination_names) if destination_names else "No destination provided"
    selected_destination_text = selected_destination.name if selected_destination else "No destination selected"
    return f"""TASK
Create section 1 (Day-by-Day Itinerary) as JSON.

OUTPUT CONTRACT
- Return valid JSON only.
- No markdown, no code fences, no extra keys, no commentary.

JSON SCHEMA
{{
    "trip_title": "short title",
    "summary": "1-2 sentence overview",
    "days": [
        {{
            "day": 1,
            "title": "day title",
            "image_keyword": "search keyword for image",
            "morning": [{{"title": "...", "details": "..."}}],
            "afternoon": [{{"title": "...", "details": "..."}}],
            "evening": [{{"title": "...", "details": "..."}}],
            "notes": ["...", "..."]
        }}
    ]
}}
INPUTS
- Description: {planning_input.trip_description}
- Source: {source_text}
- Destinations (ordered): {destination_text}
- Selected destination for single-destination tasks: {selected_destination_text}
- Preferences: {preferences_text}
- Budget: {planning_input.budget}
- Pace: {planning_input.pace}
- Trip duration: {duration_days} days

REFERENCE CONTEXT
{context_block}

HARD REQUIREMENTS
- Return 1 object only.
- Include exactly {duration_days} day entries in the days array.
- The day numbers must run from 1 to {duration_days}.
- Keep each activity concise and practical.
- Use the trip details and context to produce realistic logistics.
- Each day must include an image_keyword for Unsplash.

image_keyword rules:
- If the location is not well-known or unclear, use general travel aesthetic keywords such as:
  - "sunset landscape"
  - "mountains nature"
  - "city skyline night"
  - "beach sunrise"
  - "street travel market"
  - "architecture travel"
- must be a plain search query string
- no punctuation except spaces
- no explanations
- no brackets
- Keep it short (3–7 words max).

FINAL CHECK (DO BEFORE RETURNING)
- JSON parses successfully.
- Day count equals {duration_days}.
- All day objects contain morning, afternoon, evening arrays and notes array.
- Output contains only the schema keys above."""


def build_extras_prompt(planning_input: TripPlanningInput, context_block: str, itinerary_data: dict) -> str:
    duration_days = planning_input.duration_days or calculate_trip_duration(planning_input.trip_description)
    preferences_text = ", ".join(planning_input.preferences) if planning_input.preferences else "No explicit preferences provided"
    source_text = planning_input.source.name if planning_input.source else "Unknown"
    destination_names = [destination.name for destination in planning_input.destinations]
    selected_destination = select_first_destination(planning_input.destinations)
    destination_text = ", ".join(destination_names) if destination_names else "No destination provided"
    selected_destination_text = selected_destination.name if selected_destination else "No destination selected"
    return f"""TASK
Create sections 2-4 (Food & Culture, Budget Breakdown, Safety & Practical Tips) as JSON.

OUTPUT CONTRACT
- Return valid JSON only.
- No markdown, no code fences, no extra keys, no commentary.

JSON SCHEMA
{{
    "food_and_culture": [
        {{"title": "...", "details": "..."}}
    ],
    "budget_breakdown": [
        {{"title": "...", "details": "..."}}
    ],
    "safety_and_practical_tips": [
        {{"title": "...", "details": "..."}}
    ]
}}

INPUTS
- Description: {planning_input.trip_description}
- Source: {source_text}
- Destinations (ordered): {destination_text}
- Selected destination for cost and route-sensitive details: {selected_destination_text}
- Preferences: {preferences_text}
- Budget: {planning_input.budget}
- Pace: {planning_input.pace}
- Trip duration: {duration_days} days

REFERENCE CONTEXT
{context_block}

ITINERARY CONTEXT FOR CONSISTENCY
{itinerary_data}

HARD REQUIREMENTS
- Return 1 object only.
- Every list item must contain both "title" and "details".
- Keep headings implicit in the JSON keys; do not emit markdown headings.
- In "budget_breakdown", each details value must be a budget range in INR, e.g. "₹12,000 - ₹18,000 (optional note)".
- Include one budget item with title exactly "Estimated Total" and details as an INR range.
- Budget categories should be practical trip categories (for example: Flights, Accommodation, Transport, Food & Entry Fees), but names can vary.
- Budget ranges must be realistic for the given duration, destination context, and budget style.
- Keep all text concise and user-friendly.
- Safety and practical tips should be location-aware when possible.

FINAL CHECK (DO BEFORE RETURNING)
- JSON parses successfully.
- Object has exactly these top-level keys: food_and_culture, budget_breakdown, safety_and_practical_tips.
- All arrays are non-empty and each item has title + details.
- "Estimated Total" exists in budget_breakdown."""
