"""Location-facing query service."""

from __future__ import annotations

from typing import Optional

from services.retrieval.service import RetrievalService, get_retrieval_service


class LocationService:
    """Service for destination retrieval operations."""

    def __init__(self, retrieval: RetrievalService):
        self.retrieval = retrieval

    async def search_destinations(self, query: str, limit: int = 5):
        return await self.retrieval.search_documents(query=query, top_k=limit)


_location_service: Optional[LocationService] = None


def get_location_service() -> LocationService:
    global _location_service
    if _location_service is None:
        _location_service = LocationService(get_retrieval_service())
    return _location_service
