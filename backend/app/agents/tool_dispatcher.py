"""Tool registry + dispatcher used by ChatAgent.

Read tools are dispatched immediately; write tools are queued as plan steps
and never invoke the provider directly during the chat turn.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker

ToolHandler = Callable[["ToolContext", dict[str, Any]], Awaitable[Any]]


@dataclass(slots=True)
class ToolContext:
    user_id: UUID
    session_id: UUID
    sessionmaker: async_sessionmaker
    wallbit_base_url: str


@dataclass(slots=True)
class ToolDef:
    name: str
    description: str
    input_schema: dict[str, Any]
    category: str  # "read" or "write"
    handler: ToolHandler | None = None  # None for write tools (queued only)


class ToolDispatcher:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDef | None:
        return self._tools.get(name)

    async def dispatch(self, name: str, args: dict[str, Any], ctx: ToolContext) -> Any:
        tool = self._tools.get(name)
        if tool is None or tool.category != "read" or tool.handler is None:
            raise KeyError(f"Tool {name} not registered or not dispatchable.")
        return await tool.handler(ctx, args)

    def as_anthropic_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
        ]
