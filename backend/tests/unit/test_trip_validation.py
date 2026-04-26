import asyncio

import pytest

from services.trip.validation import (
    _parse_json_response,
    _to_validation_response,
    validate_trip_request,
)


class FakeLLMClient:
    def __init__(self, response: str | None = None, should_raise: bool = False):
        self._response = response or "{}"
        self._should_raise = should_raise

    async def generate(self, prompt: str):
        if self._should_raise:
            raise RuntimeError("llm unavailable")
        return self._response


@pytest.mark.parametrize(
    "raw,expected_name",
    [
        (
            "```json\n{\"is_valid_request\": true, \"travel_intent\": true, \"destinations\": [{\"name\": \"Paris\", \"confidence\": 0.9}], \"preferences\": [], \"missing_fields\": [], \"message\": \"ok\"}\n```",
            "Paris",
        ),
        (
            "prefix text {\"is_valid_request\": true, \"travel_intent\": true, \"destinations\": [{\"name\": \"Tokyo\", \"confidence\": 1}], \"preferences\": [], \"missing_fields\": [], \"message\": \"ok\"} suffix",
            "Tokyo",
        ),
    ],
)
def test_parse_json_response_handles_fences_and_wrappers(raw, expected_name):
    parsed = _parse_json_response(raw)
    assert parsed["destinations"][0]["name"] == expected_name


def test_to_validation_response_dedupes_and_clamps_values():
    payload = {
        "is_valid_request": True,
        "travel_intent": True,
        "destinations": [
            {"name": "Paris", "confidence": 1.5},
            {"name": " paris ", "confidence": 0.2},
            {"name": "", "confidence": 0.8},
        ],
        "source": {"name": "Mumbai", "confidence": -2},
        "preferences": [" culture ", "food"],
        "missing_fields": [" DESTINATION "],
        "message": "  ready  ",
    }

    validation = _to_validation_response(payload)

    assert len(validation.destinations) == 1
    assert validation.destinations[0].name == "Paris"
    assert validation.destinations[0].confidence == 1.0
    assert validation.source is not None
    assert validation.source.name == "Mumbai"
    assert validation.source.confidence == 0.0
    assert validation.preferences == ["culture", "food"]
    assert validation.missing_fields == ["destination"]
    assert validation.message == "ready"


def test_validate_trip_request_injects_source_when_provided():
    llm = FakeLLMClient(
        response='{"is_valid_request": true, "travel_intent": true, "destinations": [{"name": "Bali", "confidence": 0.9}], "preferences": ["relax"], "missing_fields": [], "message": "looks good"}'
    )

    result = asyncio.run(validate_trip_request(llm, "Plan Bali trip", source_name="Ahmedabad"))

    assert result.is_valid_request is True
    assert result.source is not None
    assert result.source.name == "Ahmedabad"
    assert result.source.confidence == 1.0


def test_validate_trip_request_returns_fallback_on_llm_error():
    llm = FakeLLMClient(should_raise=True)

    result = asyncio.run(validate_trip_request(llm, "random text"))

    assert result.is_valid_request is False
    assert result.travel_intent is False
    assert result.missing_fields == ["intent", "destination"]
