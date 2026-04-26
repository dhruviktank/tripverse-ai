from services.trip.service import create_trip_from_request, get_trip_for_user, list_user_trips, apply_trip_updates, persist_plan, build_dashboard_stats
from models import Trip
from schemas.trips import SaveTripRequest
import pytest

def test_create_trip():
    request = SaveTripRequest(
        title="Test Trip",
        trip_description="Goa trip",
        budget="low",
        pace="fast",
        starting_from="Ahmedabad"
    )

    trip = create_trip_from_request("user1", request)

    assert trip.title == "Test Trip"
    assert trip.user_id == "user1"


# @pytest.mark.asyncio
# async def test_get_trip_for_user(db, mocker):
#     trip = Trip(
#         id="1",
#         user_id="user1",
#         title="Trip",
#         thumbnail_url=None,
#         trip_description="Test trip",
#         budget="low",
#         pace="fast",
#         starting_from="Ahmedabad"
#     )
#     db.add(trip)
#     await db.commit()

#     # Mock thumbnail extractor
#     mocker.patch(
#         "services.thumbnail.service.extract_thumbnail_from_trip",
#         return_value="image.jpg"
#     )

#     result = await get_trip_for_user(db, "1", "user1")

#     assert result.thumbnail_url == "image.jpg"

@pytest.mark.asyncio
async def test_list_trips(db):
    trip1 = Trip(
        user_id="user1",
        title="Trip1",
        trip_description="Test trip 1",
        budget="low",
        pace="fast",
        starting_from="Ahmedabad"
    )
    trip2 = Trip(
        user_id="user1",
        title="Trip2",
        trip_description="Test trip 2",
        budget="medium",
        pace="slow",
        starting_from="Ahmedabad"
    )

    db.add_all([trip1, trip2])
    await db.commit()

    trips = await list_user_trips(db, "user1")

    assert len(trips) == 2

from schemas.trips import UpdateTripRequest

def test_apply_updates():
    trip = Trip(title="Old")

    update = UpdateTripRequest(title="New")

    updated = apply_trip_updates(trip, update)

    assert updated.title == "New"

@pytest.mark.asyncio
async def test_persist_plan(db):
    trip = Trip(
        user_id="user1",
        title="Trip",
        trip_description="Test trip",
        budget="low",
        pace="fast",
        starting_from="Ahmedabad"
    )

    db.add(trip)
    await db.commit()

    plan = {"trip_title": "Test Plan"}

    updated = await persist_plan(trip, plan, db)

    assert updated.itinerary_data["trip_title"] == "Test Plan"

@pytest.mark.asyncio
async def test_dashboard_stats(db):
    trip = Trip(
        user_id="user1",
        title="Trip",
        status="upcoming",
        trip_description="Test trip",
        budget="low",
        pace="fast",
        starting_from="Ahmedabad"
    )
    db.add(trip)
    await db.commit()

    stats = await build_dashboard_stats(db, "user1")

    assert stats["total_trips"] == 1
    assert stats["upcoming_trips"] == 1