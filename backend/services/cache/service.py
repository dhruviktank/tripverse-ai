"""Caching service for location context documents."""

from __future__ import annotations

from typing import Optional

from services.retrieval.service import RetrievalService, get_retrieval_service
from services.travel.service import SearchService, get_search_service


class CacheService:
    """Coordinates web fetch and vector caching for locations."""

    def __init__(self, retrieval: RetrievalService, search: SearchService):
        self.retrieval = retrieval
        self.search = search

    async def ensure_location_data(self, location: str, max_results: int = 5) -> int:
        """Fetch and cache location data only when no cached vectors exist."""
        has_data = await self.retrieval.has_location_data(location)
        if has_data:
            return 0
        articles = await self.search.search_travel_articles(location=location, max_results=max_results)
        return await self.retrieval.cache_location_documents(location, articles)


_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(get_retrieval_service(), get_search_service())
    return _cache_service
