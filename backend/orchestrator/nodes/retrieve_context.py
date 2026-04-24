"""Node for retrieving context documents for trip planning."""

from __future__ import annotations

from time import perf_counter

from orchestrator.state import TripPlanningState
from services.cache.service import CacheService
from services.retrieval.service import RetrievalService
from utils import select_first_destination


def _dedupe_documents(documents):
    seen_ids: set[str] = set()
    deduped = []
    for document in documents:
        metadata = document.get("metadata") or {}
        doc_id = str(document.get("id") or metadata.get("url") or metadata.get("title") or "").strip()
        if not doc_id or doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        deduped.append(document)
    return deduped


async def run_retrieve_context(
    state: TripPlanningState,
    retrieval: RetrievalService,
    cache: CacheService,
    logger,
):
    node_started_at = perf_counter()
    try:
        selected_destination = select_first_destination(state.destinations)
        destinations_to_query = state.destinations if len(state.destinations) > 1 else ([selected_destination] if selected_destination else [])

        documents = []
        for destination in destinations_to_query:
            location = destination.name.strip().lower()
            search_query_parts = [state.trip_description, destination.name, state.budget]
            search_query = " ".join(part for part in search_query_parts if part).strip()

            check_started_at = perf_counter()
            has_cached_location_data = await retrieval.has_location_data(location)
            logger.info(
                f"[TIMING] orchestrator.retrieve_context.has_location_data={perf_counter() - check_started_at:.3f}s"
            )
            if not has_cached_location_data:
                cache_started_at = perf_counter()
                cached_count = await cache.ensure_location_data(location, max_results=5)
                logger.info(
                    f"[TIMING] orchestrator.retrieve_context.cache_location_documents={perf_counter() - cache_started_at:.3f}s"
                )
                if cached_count == 0:
                    state.errors.append(f"JIT RAG fetch returned no cacheable web documents for '{location}'.")

            search_started_at = perf_counter()
            destination_documents = await retrieval.search_documents(
                query=search_query,
                top_k=5,
                metadata_filter={"category": {"$eq": "destination_guide"}, "location": {"$eq": location}},
            )
            logger.info(
                f"[TIMING] orchestrator.retrieve_context.search_documents.location={perf_counter() - search_started_at:.3f}s"
            )
            documents.extend(destination_documents)

        if not documents and selected_destination:
            fallback_started_at = perf_counter()
            fallback_query = " ".join(
                part for part in [state.trip_description, selected_destination.name, state.budget] if part
            ).strip()
            documents = await retrieval.search_documents(
                query=fallback_query,
                top_k=5,
                metadata_filter={"category": {"$eq": "destination_guide"}},
            )
            logger.info(
                f"[TIMING] orchestrator.retrieve_context.search_documents.fallback={perf_counter() - fallback_started_at:.3f}s"
            )

        documents = _dedupe_documents(documents)
        state.context_documents = documents
        logger.info(f"[TIMING] orchestrator.retrieve_context.total={perf_counter() - node_started_at:.3f}s docs={len(documents)}")
        return {"context_documents": documents}
    except Exception as exc:
        state.errors.append(f"Context retrieval error: {exc}")
        logger.info(f"[TIMING] orchestrator.retrieve_context.total={perf_counter() - node_started_at:.3f}s (exception)")
        return {}
