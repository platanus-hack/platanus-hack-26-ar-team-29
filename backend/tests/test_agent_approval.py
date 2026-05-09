from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.agents.approval import ApprovalBridge, PermissionResultAllow, PermissionResultDeny
from app.agents.events import AgentEvent


@pytest.mark.asyncio
async def test_read_wallbit_tools_auto_allow() -> None:
    bridge = ApprovalBridge()

    result = await bridge.can_use_tool(
        "mcp__wallbit__get_checking_balance",
        {"account": "default"},
    )

    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input == {"account": "default"}


@pytest.mark.asyncio
async def test_write_wallbit_tool_emits_approval_and_allows_on_confirm() -> None:
    events: list[AgentEvent] = []
    bridge = ApprovalBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(
        bridge.can_use_tool("mcp__wallbit__create_trade", {"symbol": "SPY"})
    )
    await _wait_for_events(events, 1)

    approval = events[0]
    assert approval.type == "approval_requested"
    assert approval.payload["tool_name"] == "mcp__wallbit__create_trade"

    assert bridge.resolve(approval.payload["approval_id"], "confirm")
    result = await task

    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input == {"symbol": "SPY"}
    assert events[-1].type == "approval_resolved"
    assert events[-1].payload["decision"] == "confirm"


@pytest.mark.asyncio
async def test_write_wallbit_tool_denies_on_reject() -> None:
    events: list[AgentEvent] = []
    bridge = ApprovalBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(
        bridge.can_use_tool("mcp__wallbit__create_trade", {"symbol": "SPY"})
    )
    await _wait_for_events(events, 1)

    assert bridge.resolve(events[0].payload["approval_id"], "reject")
    result = await task

    assert isinstance(result, PermissionResultDeny)
    assert result.message == "User rejected this action"


@pytest.mark.asyncio
async def test_unknown_wallbit_tool_requires_approval() -> None:
    events: list[AgentEvent] = []
    bridge = ApprovalBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(
        bridge.can_use_tool("mcp__wallbit__future_write", {"value": 1})
    )
    await _wait_for_events(events, 1)

    assert events[0].type == "approval_requested"
    assert bridge.resolve(events[0].payload["approval_id"], "reject")
    await task


def _collecting_sink(events: list[AgentEvent]):
    async def sink(event: AgentEvent) -> None:
        events.append(event)

    return sink


async def _wait_for_events(events: list[Any], count: int) -> None:
    for _ in range(20):
        if len(events) >= count:
            return
        await asyncio.sleep(0.01)
    raise AssertionError(f"expected {count} events, got {len(events)}")

