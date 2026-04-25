"""Gemini and Grok-compatible chat LLM client."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from core.config import get_settings
from llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Provider-backed client for text generation."""

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(str(text))
                else:
                    parts.append(str(item))
            return "\n".join([p for p in parts if p]).strip()
        if content is None:
            return ""
        return str(content)

    def __init__(self):
        settings = get_settings()
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature

        if self.provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError as exc:
                raise ImportError(
                    "Gemini support requires 'langchain-google-genai'. Install it with: pip install langchain-google-genai"
                ) from exc
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                google_api_key=settings.gemini_api_key,
                max_retries=settings.max_retries,
                timeout=settings.request_timeout,
            )
        elif self.provider == "grok":
            try:
                from langchain_groq import ChatGroq
            except ImportError as exc:
                raise ImportError(
                    "Grok support requires 'langchain-groq'. Install it with: pip install langchain-groq"
                ) from exc
            self.llm = ChatGroq(
                model=self.model,
                temperature=self.temperature,
                api_key=settings.grok_api_key,
                max_retries=settings.max_retries,
                timeout=settings.request_timeout,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages: List[BaseMessage] = []
        if system_prompt:
            if self.model == "gemma-3-27b-it":
                prompt = f"{system_prompt}\n\n{prompt}"
            else:
                messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages, **kwargs)
        return self._normalize_content(response.content)

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        response = await self.generate(prompt, system_prompt, **kwargs)
        return {"response": response}

    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        messages: List[BaseMessage] = []
        if system_prompt:
            if self.model == "gemma-3-27b-it":
                prompt = f"{system_prompt}\n\n{prompt}"
            else:
                messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        for chunk in self.llm.stream(messages, **kwargs):
            normalized = self._normalize_content(getattr(chunk, "content", ""))
            if normalized:
                yield normalized
