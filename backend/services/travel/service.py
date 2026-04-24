"""External travel search service."""

from __future__ import annotations

import asyncio
import importlib
import re
from html import unescape
from typing import Any, Dict, List, Optional

import httpx

from core.config import get_settings


class SearchService:
    """Fetch travel content from web search providers."""

    def __init__(self) -> None:
        settings = get_settings()
        self.provider = settings.search_provider.lower().strip()
        self.tavily_api_key = settings.tavily_api_key
        self.serper_api_key = settings.serper_api_key
        self.max_article_chars = settings.max_article_chars
        self.request_timeout = settings.request_timeout

    @staticmethod
    def _clean_text(text: Optional[str], max_chars: int) -> str:
        if not text:
            return ""
        cleaned = unescape(text)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:max_chars]

    async def _search_tavily(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.tavily_api_key:
            return []

        try:
            tavily_module = importlib.import_module("tavily")
            async_tavily_client = getattr(tavily_module, "AsyncTavilyClient")
        except Exception:
            return []

        client = async_tavily_client(api_key=self.tavily_api_key)
        queries = [
            f"top attractions and itinerary {destination}",
            f"{destination} food and culture guide",
            f"{destination} travel tips and cost",
        ]

        responses = await asyncio.gather(
            *(client.search(q, max_results=max_results) for q in queries),
            return_exceptions=True,
        )

        all_results: List[Dict[str, Any]] = []
        for source_query, response in zip(queries, responses):
            if isinstance(response, Exception):
                continue
            for item in response.get("results", []):
                item["source_query"] = source_query
                all_results.append(item)

        deduplicated: List[Dict[str, Any]] = []
        seen_urls: set[str] = set()
        sorted_results = sorted(all_results, key=lambda x: float(x.get("score", 0.0)), reverse=True)
        for item in sorted_results:
            url = (item.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            content = item.get("raw_content") or item.get("content") or ""
            cleaned = self._clean_text(content, self.max_article_chars)
            if len(cleaned) < 80:
                continue
            deduplicated.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": url,
                    "content": cleaned,
                    "source": "tavily",
                    "source_query": item.get("source_query", ""),
                    "score": float(item.get("score", 0.0)),
                }
            )
            if len(deduplicated) >= 5:
                break

        return deduplicated

    async def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.serper_api_key:
            return []

        headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": max_results}
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            response = await client.post("https://google.serper.dev/search", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("organic", []):
            content = item.get("snippet") or ""
            cleaned = self._clean_text(content, self.max_article_chars)
            if len(cleaned) < 40:
                continue
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("link", ""),
                    "content": cleaned,
                    "source": "serper",
                }
            )
        return results

    async def search_travel_articles(self, location: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if self.provider == "serper":
            query = f"{location} travel guide itinerary best places local tips"
            return await self._search_serper(query=query, max_results=max_results)
        return await self._search_tavily(destination=location, max_results=max_results)


_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
