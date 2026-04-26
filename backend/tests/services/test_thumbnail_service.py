import pytest
from unittest.mock import AsyncMock, Mock, patch

from services.thumbnail.service import (
    fetch_unsplash_image,
    enrich_itinerary_with_images,
    extract_thumbnail_url,
    extract_thumbnail_from_trip,
)

@pytest.mark.asyncio
async def test_fetch_unsplash_image_empty_keyword():
    result = await fetch_unsplash_image("")
    assert result == ""


@pytest.mark.asyncio
async def test_fetch_unsplash_image_exception():
    async_client_mock = AsyncMock()
    async_client_mock.get.side_effect = AsyncMock(side_effect=Exception("Crash"))

    with patch("httpx.AsyncClient", return_value=async_client_mock):
        with pytest.raises(Exception):
            await fetch_unsplash_image("Paris")


# ================= ENRICH ITINERARY =================

@pytest.mark.asyncio
async def test_enrich_itinerary_with_images_success():
    itinerary = {
        "days": [
            {"day": 1, "image_keyword": "Paris"},
            {"day": 2, "image_keyword": "London"},
        ]
    }

    with patch(
        "services.thumbnail.service.fetch_unsplash_image",
        new=AsyncMock(side_effect=["img1.jpg", "img2.jpg"])
    ):
        result = await enrich_itinerary_with_images(itinerary)

    assert result["days"][0]["thumbnail_url"] == "img1.jpg"
    assert result["days"][1]["thumbnail_url"] == "img2.jpg"


@pytest.mark.asyncio
async def test_enrich_itinerary_with_images_failure():
    itinerary = {
        "days": [
            {"day": 1, "image_keyword": "Paris"}
        ]
    }

    with patch(
        "services.thumbnail.service.fetch_unsplash_image",
        new=AsyncMock(side_effect=Exception("fail"))
    ):
        result = await enrich_itinerary_with_images(itinerary)

    assert result["days"][0]["thumbnail_url"] == ""


@pytest.mark.asyncio
async def test_enrich_itinerary_no_days():
    itinerary = {}

    result = await enrich_itinerary_with_images(itinerary)

    assert result == {}


# ================= EXTRACT THUMBNAIL URL =================

def test_extract_thumbnail_url_day1_priority():
    data = {
        "itinerary": {
            "days": [
                {"day": 1, "thumbnail_url": "day1.jpg"},
                {"day": 2, "thumbnail_url": "day2.jpg"},
            ]
        }
    }

    assert extract_thumbnail_url(data) == "day1.jpg"


def test_extract_thumbnail_url_fallback():
    data = {
        "itinerary": {
            "days": [
                {"day": 2, "thumbnail_url": "day2.jpg"}
            ]
        }
    }

    assert extract_thumbnail_url(data) == "day2.jpg"


def test_extract_thumbnail_url_no_images():
    data = {
        "itinerary": {
            "days": [{"day": 1}]
        }
    }

    assert extract_thumbnail_url(data) is None


def test_extract_thumbnail_url_empty():
    assert extract_thumbnail_url(None) is None


# ================= EXTRACT FROM TRIP =================

class DummyTrip:
    def __init__(self, thumbnail_url=None, itinerary_data=None):
        self.thumbnail_url = thumbnail_url
        self.itinerary_data = itinerary_data


def test_extract_thumbnail_from_trip_existing_thumbnail():
    trip = DummyTrip(thumbnail_url="existing.jpg")

    assert extract_thumbnail_from_trip(trip) == "existing.jpg"


def test_extract_thumbnail_from_trip_day1():
    trip = DummyTrip(
        itinerary_data={
            "itinerary": {
                "days": [
                    {"day": 1, "thumbnail_url": "day1.jpg"}
                ]
            }
        }
    )

    assert extract_thumbnail_from_trip(trip) == "day1.jpg"


def test_extract_thumbnail_from_trip_fallback():
    trip = DummyTrip(
        itinerary_data={
            "itinerary": {
                "days": [
                    {"day": 2, "thumbnail_url": "day2.jpg"}
                ]
            }
        }
    )

    assert extract_thumbnail_from_trip(trip) == "day2.jpg"


def test_extract_thumbnail_from_trip_invalid_days():
    trip = DummyTrip(
        itinerary_data={"itinerary": {"days": "invalid"}}
    )

    assert extract_thumbnail_from_trip(trip) is None


def test_extract_thumbnail_from_trip_no_data():
    trip = DummyTrip()

    assert extract_thumbnail_from_trip(trip) is None
