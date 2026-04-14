"""External search client for on-the-fly RAG document collection."""

import re
from html import unescape
from typing import Dict, Any, List, Optional

import httpx

from config import get_settings


class SearchClient:
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

    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        if not self.tavily_api_key:
            return []

        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_raw_content": True,
        }
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("results", []):
            content = item.get("raw_content") or item.get("content") or ""
            cleaned = self._clean_text(content, self.max_article_chars)
            if len(cleaned) < 80:
                continue
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("url", ""),
                    "content": cleaned,
                    "source": "tavily",
                }
            )
        return results

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
        """Fetch top web articles for a location to support JIT RAG caching."""
        query = f"{location} travel guide itinerary best places local tips"

        if self.provider == "serper":
            return await self._search_serper(query=query, max_results=max_results)
        return await self._search_tavily(query=query, max_results=max_results)


_search_client: Optional[SearchClient] = None


def get_search_client() -> SearchClient:
    global _search_client
    if _search_client is None:
        _search_client = SearchClient()
    return _search_client
