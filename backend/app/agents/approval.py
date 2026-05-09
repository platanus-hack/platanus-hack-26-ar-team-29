from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from app.agents.events import (
    AgentEvent,
    approval_requested_event,
    approval_resolved_event,
)

try:  # pragma: no cover - exercised only when the SDK is installed.
    from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny
except ImportError:  # pragma: no cover - local fallback keeps tests importable.

    @dataclass(frozen=True)
    class PermissionResultAllow:  # type: ignore[no-redef]
        behavior: str = "allow"
        updated_input: dict[str, Any] | None = None
        updated_permissions: list[Any] | None = None

    @dataclass(frozen=True)
    class PermissionResultDeny:  # type: ignore[no-redef]
        behavior: str = "deny"
        message: str = ""


READ_WALLBIT_TOOLS = {
    "mcp__wallbit__get_checking_balance",
    "mcp__wallbit__get_stocks_balance",
    "mcp__wallbit__list_transactions",
    "mcp__wallbit__get_asset",
}

WRITE_WALLBIT_TOOLS = {
    "mcp__wallbit__create_trade",
}

from typing import Union
ApprovalResult = Union[PermissionResultAllow, PermissionResultDeny]
EventSink = Callable[[AgentEvent], Awaitable[None]]


def requires_approval(tool_name: str) -> bool:
    if tool_name in READ_WALLBIT_TOOLS:
        return False
    if tool_name in WRITE_WALLBIT_TOOLS:
        return True
    return tool_name.startswith("mcp__wallbit__")


class ApprovalBridge:
    def __init__(self) -> None:
        self._event_sink: EventSink | None = None
        self._pending: dict[str, asyncio.Future[str]] = {}

    def set_event_sink(self, event_sink: EventSink) -> None:
        self._event_sink = event_sink

    def clear_event_sink(self) -> None:
        self._event_sink = None

    async def can_use_tool(
        self,
        tool_name: str,
        input_data: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> ApprovalResult:
        del options

        if not requires_approval(tool_name):
            return PermissionResultAllow(updated_input=input_data)

        if self._event_sink is None:
            return PermissionResultDeny(
                message="No approval channel is available for this action."
            )

        approval_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str] = loop.create_future()
        self._pending[approval_id] = future

        await self._event_sink(
            approval_requested_event(
                approval_id=approval_id,
                tool_name=tool_name,
                input_data=input_data,
            )
        )

        try:
            decision = await future
        finally:
            self._pending.pop(approval_id, None)

        await self._event_sink(
            approval_resolved_event(
                approval_id=approval_id,
                tool_name=tool_name,
                decision=decision,
            )
        )

        if decision == "confirm":
            return PermissionResultAllow(updated_input=input_data)
        return PermissionResultDeny(message="User rejected this action")

    def resolve(self, approval_id: str, decision: str) -> bool:
        normalized = decision.strip().lower()
        if normalized not in {"confirm", "reject"}:
            raise ValueError("decision must be 'confirm' or 'reject'")

        future = self._pending.get(approval_id)
        if future is None or future.done():
            return False
        future.set_result(normalized)
        return True
