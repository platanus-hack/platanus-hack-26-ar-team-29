"""Thin wrapper around the Anthropic SDK.

Isolates the rest of the codebase from the SDK so swapping/upgrading is local.
We use the non-streaming `messages.create` for tool-use turns (more robust)
and stream tokens manually after the model is done with tool calls.
"""

from __future__ import annotations

from typing import Any

import anthropic
import structlog

log = structlog.get_logger(__name__)


class AnthropicClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._client: anthropic.AsyncAnthropic | None = None
        if api_key:
            self._client = anthropic.AsyncAnthropic(api_key=api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    async def messages_create(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1500,
        temperature: float = 0.4,
    ) -> Any:
        if self._client is None:
            raise RuntimeError("Anthropic client unavailable; ANTHROPIC_API_KEY not set.")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "system": system,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        return await self._client.messages.create(**kwargs)
