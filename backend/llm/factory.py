"""Factory for LLM client instances."""

from __future__ import annotations

from typing import Optional

from llm.base import BaseLLMClient
from llm.gemini_client import GeminiClient

_llm_client: Optional[BaseLLMClient] = None


def get_llm_client() -> BaseLLMClient:
    """Get or create the configured LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = GeminiClient()
    return _llm_client
