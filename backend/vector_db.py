"""Vector database client for storing and retrieving embeddings."""

import time
import uuid
from typing import Optional, List, Dict, Any
from config import get_settings


class VectorDatabaseClient:
    """Client for interacting with vector databases."""
    
    def __init__(self):
        """Initialize the vector database client."""
        settings = get_settings()
        self.embedding_dimension = settings.embedding_dimension
        self._init_provider(settings)

        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError as exc:
            raise ImportError(
                "Gemini embeddings require 'langchain-google-genai'. Install it with: pip install langchain-google-genai"
            ) from exc

        # Force embedding output size to match Pinecone index dimension.
        # This prevents vector dimension mismatch errors during upsert/query.
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
        """Parse Pinecone environment into (cloud, region).

        Supports both:
        - legacy format: us-west-2-aws
        - region-only format: us-east-1 (defaults cloud to aws)
        """
        normalized = (environment or "").strip()
        if not normalized:
            return "aws", "us-east-1"

        parts = normalized.split("-")
        # legacy: <region>-<cloud>
        if parts[-1] in {"aws", "gcp", "azure"} and len(parts) >= 4:
            return parts[-1], "-".join(parts[:-1])

        # region only
        return "aws", normalized

    def _ensure_index_exists(self, settings) -> None:
        """Create the Pinecone index if it doesn't exist."""
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

        # Wait briefly until the index is available.
        for _ in range(30):
            if settings.pinecone_index_name in self.client.list_indexes().names():
                return
            time.sleep(1)

        raise RuntimeError(
            f"Pinecone index '{settings.pinecone_index_name}' was created but is not ready yet."
        )
    
    def _init_provider(self, settings) -> None:
        """Initialize Pinecone vector database."""
        try:
            from pinecone import Pinecone
            self.client = Pinecone(
                api_key=settings.pinecone_api_key
            )
            self._ensure_index_exists(settings)
            self.index = self.client.Index(settings.pinecone_index_name)
        except ImportError:
            raise ImportError("Pinecone not installed. Install with: pip install pinecone")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        embedding = self.embeddings.embed_query(text)
        return embedding
    
    async def store_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store a document with its embedding in Pinecone."""
        try:
            embedding = await self.embed_text(text)
            self.index.upsert(
                vectors=[
                    {
                        "id": document_id,
                        "values": embedding,
                        "metadata": metadata or {},
                    }
                ]
            )
            return True
        except Exception as e:
            print(f"Error storing document: {e}")
            return False
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in Pinecone based on query."""
        try:
            query_embedding = await self.embed_text(query)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=metadata_filter
            )
            return [
                {
                    "id": getattr(match, "id", None),
                    "score": getattr(match, "score", None),
                    "metadata": getattr(match, "metadata", {}),
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    async def has_location_data(self, location: str) -> bool:
        """Check whether Pinecone already contains travel docs for a location."""
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
        """Embed and cache fetched web articles in Pinecone for JIT RAG."""
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
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from Pinecone."""
        try:
            self.index.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False


# Global instance
_vector_db_client: Optional[VectorDatabaseClient] = None


def get_vector_db_client() -> VectorDatabaseClient:
    """Get or create the vector database client."""
    global _vector_db_client
    if _vector_db_client is None:
        _vector_db_client = VectorDatabaseClient()
    return _vector_db_client
