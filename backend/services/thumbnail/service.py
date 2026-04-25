import httpx
from typing import Dict, Any, Optional
from models import Trip
UNSPLASH_ACCESS_KEY = "jisNRnLKLzkMd106mRsCk9jWjJetGrgClWTweHbKO2U"


async def fetch_unsplash_image(keyword: str) -> str:
    """Fetch a single image URL from Unsplash."""
    if not keyword:
        return ""

    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": "landscape",
    }

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return ""

        return results[0]["urls"]["regular"]


async def enrich_itinerary_with_images(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """Add Unsplash image URLs to each day in itinerary."""

    for day in itinerary.get("days", []):
        keyword = day.get("image_keyword")

        try:
            thumbnail_url = await fetch_unsplash_image(keyword)
            day["thumbnail_url"] = thumbnail_url
        except Exception as e:
            day["thumbnail_url"] = ""
            print(f"Failed for keyword '{keyword}': {e}")

    return itinerary

def extract_thumbnail_url(itinerary_data: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Picks a thumbnail image from itinerary days.
    Priority: Day 1 → fallback to first available image_url.
    """

    if not itinerary_data:
        return None

    # safely get nested itinerary
    itinerary = itinerary_data.get("itinerary")
    if not itinerary:
        return None

    days = itinerary.get("days", [])
    if not days:
        return None

    # Prefer Day 1 image
    for day in days:
        if day.get("day") == 1 and day.get("thumbnail_url"):
            return day["thumbnail_url"]

    # Fallback: first available image
    for day in days:
        if day.get("thumbnail_url"):
            return day["thumbnail_url"]

    return None

from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


def extract_thumbnail_from_trip(trip: Trip) -> str | None:
    """Extract thumbnail from itinerary if missing."""

    if trip.thumbnail_url:
        return trip.thumbnail_url

    if not trip.itinerary_data:
        return None

    itinerary = trip.itinerary_data.get("itinerary", {})
    days = itinerary.get("days", [])

    if not isinstance(days, list):
        return None

    # Prefer Day 1
    for day in days:
        if day.get("day") == 1 and day.get("thumbnail_url"):
            return day["thumbnail_url"]

    # fallback
    for day in days:
        if day.get("thumbnail_url"):
            return day["thumbnail_url"]

    return None