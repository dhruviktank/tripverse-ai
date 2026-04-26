import pytest
from unittest.mock import AsyncMock, MagicMock

from orchestrator.graph import TripPlanningOrchestrator


# ================= FIXTURE =================

@pytest.fixture
def orchestrator(mocker):
    """Create orchestrator with all external dependencies mocked."""

    # Mock settings
    mocker.patch("orchestrator.graph.get_settings", return_value=MagicMock())

    # Mock LLM
    fake_llm = AsyncMock()
    fake_llm.generate = AsyncMock(return_value='{"itinerary": {"days": []}}')
    mocker.patch("orchestrator.graph.get_llm_client", return_value=fake_llm)

    # Mock retrieval + cache
    mocker.patch("orchestrator.graph.get_retrieval_service", return_value=AsyncMock())
    mocker.patch("orchestrator.graph.get_cache_service", return_value=AsyncMock())

    # Mock graph to avoid LangGraph execution
    fake_graph = AsyncMock()
    fake_graph.ainvoke = AsyncMock(return_value={"final_plan": {"ok": True}})

    orch = TripPlanningOrchestrator()
    orch.graph = fake_graph

    return orch

# ================= INVALID REQUEST =================

@pytest.mark.asyncio
async def test_plan_trip_invalid_request(orchestrator):
    orchestrator.graph.ainvoke = AsyncMock(
        return_value={
            "is_request_valid": False,
            "validation": {"message": "Invalid"},
            "requires_destination": True,
        }
    )

    result = await orchestrator.plan_trip({})

    assert result["success"] is False
    assert result["requires_destination"] is True


# ================= EXCEPTION CASE =================

@pytest.mark.asyncio
async def test_plan_trip_exception(orchestrator):
    orchestrator.graph.ainvoke.side_effect = AsyncMock(side_effect=Exception("Crash"))

    result = await orchestrator.plan_trip({})

    assert result["success"] is False
    assert "Crash" in result["error"]


# ================= STREAM VALIDATION FAIL =================

@pytest.mark.asyncio
async def test_plan_trip_stream_validation_fail(orchestrator):
    orchestrator._validate_request = AsyncMock(
        return_value={
            "is_request_valid": False,
            "validation": {"message": "Invalid"},
        }
    )

    trip_input = {}

    events = []
    async for event in orchestrator.plan_trip_stream(trip_input):
        events.append(event)

    assert events[0]["event"] == "validation"
    assert events[0]["success"] is False


# ================= STREAM EXCEPTION =================

@pytest.mark.asyncio
async def test_plan_trip_stream_exception(orchestrator):
    orchestrator._validate_request = AsyncMock(side_effect=Exception("Crash"))

    events = []
    async for event in orchestrator.plan_trip_stream({}):
        events.append(event)

    assert events[-1]["event"] == "error"
    assert "Crash" in events[-1]["error"]