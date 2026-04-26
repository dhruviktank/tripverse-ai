import pytest
from httpx import AsyncClient
from main import app
import httpx

@pytest.mark.asyncio
async def test_full_trip_flow():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/trips/plan",
            json={
                "trip_description": "Trip to Goa",
                "duration_days": 1,
                "preferences": ["beach", "food"],
                "budget": "Balanced",
                "pace": "Balanced",
                "starting_from": "Ahmedabad",
                "confirm_intent": True
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True
        assert "plan" in data

@pytest.mark.asyncio
async def test_chat_to_plan_flow():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        session_id = "test-session"

        # Step 1: Send message
        res1 = await client.post("/api/chat", json={
            "session_id": session_id,
            "message": "I want to go to Manali for 4 days"
        })

        assert res1.status_code == 200

        # Step 2: Generate plan
        # res2 = await client.post(f"/api/chat/{session_id}/plan")

        # data = res2.json()

        # assert data["success"] is True