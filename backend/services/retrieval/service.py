"""Vector retrieval service backed by Pinecone."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from core.config import get_settings


class RetrievalService:
    """Service for embedding, vector storage, and semantic retrieval."""

    def __init__(self):
        settings = get_settings()
        self.embedding_dimension = settings.embedding_dimension
        self._init_provider(settings)

        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError as exc:
            raise ImportError(
                "Gemini embeddings require 'langchain-google-genai'. Install it with: pip install langchain-google-genai"
            ) from exc

        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,
                google_api_key=settings.gemini_api_key,
                output_dimensionality=self.embedding_dimension,
            )
        except TypeError:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=settings.embedding_model,
                    google_api_key=settings.gemini_api_key,
                    dimensions=self.embedding_dimension,
                )
            except TypeError:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=settings.embedding_model,
                    google_api_key=settings.gemini_api_key,
                )

    def _parse_serverless_environment(self, environment: str) -> tuple[str, str]:
        normalized = (environment or "").strip()
        if not normalized:
            return "aws", "us-east-1"

        parts = normalized.split("-")
        if parts[-1] in {"aws", "gcp", "azure"} and len(parts) >= 4:
            return parts[-1], "-".join(parts[:-1])

        return "aws", normalized

    def _ensure_index_exists(self, settings) -> None:
        existing_indexes = self.client.list_indexes().names()
        if settings.pinecone_index_name in existing_indexes:
            index_description = self.client.describe_index(settings.pinecone_index_name)
            index_dimension = None
            if hasattr(index_description, "dimension"):
                index_dimension = getattr(index_description, "dimension")
            elif isinstance(index_description, dict):
                index_dimension = index_description.get("dimension")

            if index_dimension:
                self.embedding_dimension = int(index_dimension)
            return

        from pinecone import ServerlessSpec

        cloud, region = self._parse_serverless_environment(settings.pinecone_environment)
        self.client.create_index(
            name=settings.pinecone_index_name,
            dimension=self.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )

        for _ in range(30):
            if settings.pinecone_index_name in self.client.list_indexes().names():
                return
            time.sleep(1)

        raise RuntimeError(f"Pinecone index '{settings.pinecone_index_name}' was created but is not ready yet.")

    def _init_provider(self, settings) -> None:
        try:
            from pinecone import Pinecone
        except ImportError as exc:
            raise ImportError("Pinecone not installed. Install with: pip install pinecone") from exc

        self.client = Pinecone(api_key=settings.pinecone_api_key)
        self._ensure_index_exists(settings)
        self.index = self.client.Index(settings.pinecone_index_name)

    async def embed_text(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = await self.embed_text(query)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=metadata_filter,
            )
            return [
                {
                    "id": getattr(match, "id", None),
                    "score": getattr(match, "score", None),
                    "metadata": getattr(match, "metadata", {}),
                }
                for match in results.matches
            ]
        except Exception:
            return []

    async def has_location_data(self, location: str) -> bool:
        if not location:
            return False
        normalized = location.strip().lower()
        probe_query = f"{normalized} travel guide"
        results = await self.search_documents(
            query=probe_query,
            top_k=1,
            metadata_filter={"location": {"$eq": normalized}},
        )
        return len(results) > 0

    async def cache_location_documents(self, location: str, articles: List[Dict[str, Any]]) -> int:
        if not location or not articles:
            return 0

        normalized = location.strip().lower()
        vectors: List[Dict[str, Any]] = []
        for idx, article in enumerate(articles):
            content = (article.get("content") or "").strip()
            if len(content) < 40:
                continue

            embedding = await self.embed_text(content)
            article_url = article.get("url") or f"local-{idx}"
            stable_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{normalized}-{article_url}")
            vectors.append(
                {
                    "id": f"travel-{stable_id}",
                    "values": embedding,
                    "metadata": {
                        "location": normalized,
                        "category": "destination_guide",
                        "title": article.get("title", "Untitled"),
                        "url": article.get("url", ""),
                        "source": article.get("source", "web"),
                        "content": content[:1200],
                    },
                }
            )

        if not vectors:
            return 0

        self.index.upsert(vectors=vectors)
        return len(vectors)


_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
