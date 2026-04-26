from api.routes import chat as chat_routes
from api.routes import planning as planning_routes


class FakeOrchestratorSuccess:
    async def plan_trip(self, trip_input):
        return {
            "success": True,
            "plan": {
                "itinerary": {
                    "days": [
                        {"day": 1, "title": "Arrival"},
                    ]
                }
            },
            "errors": None,
        }


class FakeOrchestratorValidationFailure:
    async def plan_trip(self, trip_input):
        return {
            "success": False,
            "error": "Destination missing",
            "errors": None,
            "validation": {
                "source": None,
                "destinations": [],
            },
            "requires_confirmation": False,
            "requires_destination": True,
        }


def _plan_payload():
    return {
        "trip_description": "Plan a 5 day trip to Kyoto",
        "duration_days": 5,
        "preferences": ["culture"],
        "budget": "Balanced",
        "pace": "Relaxed",
        "starting_from": "Mumbai",
        "confirm_intent": False,
    }


def test_plan_trip_success(client, monkeypatch):
    monkeypatch.setattr(planning_routes, "get_trip_planning_orchestrator", lambda: FakeOrchestratorSuccess())

    response = client.post("/api/trips/plan", json=_plan_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "plan" in body
    assert body["plan"]["itinerary"]["days"][0]["title"] == "Arrival"


def test_plan_trip_validation_failure(client, monkeypatch):
    monkeypatch.setattr(planning_routes, "get_trip_planning_orchestrator", lambda: FakeOrchestratorValidationFailure())

    response = client.post("/api/trips/plan", json=_plan_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["requires_destination"] is True
    assert body["validation"]["destinations"] == []


def test_generate_plan_from_chat_success(client, monkeypatch):
    async def fake_get_session_info(session_id):
        return {"session_id": session_id}

    async def fake_generate_plan_from_context(session_id):
        return {"success": True, "plan": {"itinerary": {"days": []}}}

    monkeypatch.setattr(chat_routes.chat_service, "get_session_info", fake_get_session_info)
    monkeypatch.setattr(chat_routes.chat_service, "generate_plan_from_context", fake_generate_plan_from_context)

    response = client.post("/api/chat/plan/test-session")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["session_id"] == "test-session"
    assert "plan" in body