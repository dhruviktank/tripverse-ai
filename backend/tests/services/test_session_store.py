import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.thumbnail.service import (
    fetch_unsplash_image,
    enrich_itinerary_with_images,
    extract_thumbnail_url,
    extract_thumbnail_from_trip,
)


# ================= FETCH UNSPLASH =================

@pytest.mark.asyncio
@patch("services.thumbnail.service.httpx.AsyncClient")
async def test_fetch_unsplash_image_success(mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"urls": {"regular": "http://image.jpg"}}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

    result = await fetch_unsplash_image("Goa")

    assert result == "http://image.jpg"


@pytest.mark.asyncio
@patch("services.thumbnail.service.httpx.AsyncClient")
async def test_fetch_unsplash_image_no_results(mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status = MagicMock()

    mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

    result = await fetch_unsplash_image("Unknown")

    assert result == ""


@pytest.mark.asyncio
async def test_fetch_unsplash_image_empty_keyword():
    result = await fetch_unsplash_image("")
    assert result == ""


# ================= ENRICH ITINERARY =================

@pytest.mark.asyncio
@patch("services.thumbnail.service.fetch_unsplash_image", new_callable=AsyncMock)
async def test_enrich_itinerary_success(mock_fetch):
    mock_fetch.return_value = "http://img.jpg"

    itinerary = {
        "days": [
            {"day": 1, "image_keyword": "Goa"},
            {"day": 2, "image_keyword": "Beach"},
        ]
    }

    result = await enrich_itinerary_with_images(itinerary)

    assert result["days"][0]["thumbnail_url"] == "http://img.jpg"
    assert result["days"][1]["thumbnail_url"] == "http://img.jpg"


@pytest.mark.asyncio
@patch("services.thumbnail.service.fetch_unsplash_image", new_callable=AsyncMock)
async def test_enrich_itinerary_exception(mock_fetch):
    mock_fetch.side_effect = AsyncMock(side_effect=Exception("Crash"))

    itinerary = {
        "days": [
            {"day": 1, "image_keyword": "Goa"}
        ]
    }

    result = await enrich_itinerary_with_images(itinerary)

    assert result["days"][0]["thumbnail_url"] == ""


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
                {"day": 2, "thumbnail_url": "day2.jpg"},
            ]
        }
    }

    assert extract_thumbnail_url(data) == "day2.jpg"


def test_extract_thumbnail_url_no_data():
    assert extract_thumbnail_url(None) is None
    assert extract_thumbnail_url({}) is None


# ================= EXTRACT FROM TRIP =================

class FakeTrip:
    def __init__(self, thumbnail_url=None, itinerary_data=None):
        self.thumbnail_url = thumbnail_url
        self.itinerary_data = itinerary_data


def test_extract_thumbnail_from_trip_existing():
    trip = FakeTrip(thumbnail_url="existing.jpg")

    assert extract_thumbnail_from_trip(trip) == "existing.jpg"


def test_extract_thumbnail_from_trip_day1():
    trip = FakeTrip(
        itinerary_data={
            "itinerary": {
                "days": [
                    {"day": 1, "thumbnail_url": "day1.jpg"},
                    {"day": 2, "thumbnail_url": "day2.jpg"},
                ]
            }
        }
    )

    assert extract_thumbnail_from_trip(trip) == "day1.jpg"


def test_extract_thumbnail_from_trip_fallback():
    trip = FakeTrip(
        itinerary_data={
            "itinerary": {
                "days": [
                    {"day": 2, "thumbnail_url": "day2.jpg"},
                ]
            }
        }
    )

    assert extract_thumbnail_from_trip(trip) == "day2.jpg"


def test_extract_thumbnail_from_trip_invalid():
    trip = FakeTrip(itinerary_data=None)

    assert extract_thumbnail_from_trip(trip) is None