"""Base LLM interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLMClient(ABC):
    """Abstract contract for LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        raise NotImplementedError
