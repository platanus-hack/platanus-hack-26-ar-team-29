from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.agents.events import AgentEvent
from app.agents.interactions import (
    PermissionResultAllow,
    PermissionResultDeny,
    UserInteractionBridge,
)


@pytest.mark.asyncio
async def test_read_wallbit_tools_auto_allow() -> None:
    bridge = UserInteractionBridge()

    result = await bridge.can_use_tool(
        "mcp__wallbit__get_checking_balance",
        {"account": "default"},
    )

    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input == {"account": "default"}


@pytest.mark.asyncio
async def test_write_wallbit_tool_emits_approval_and_allows_on_confirm() -> None:
    events: list[AgentEvent] = []
    bridge = UserInteractionBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(bridge.can_use_tool("mcp__wallbit__create_trade", {"symbol": "SPY"}))
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
    bridge = UserInteractionBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(bridge.can_use_tool("mcp__wallbit__create_trade", {"symbol": "SPY"}))
    await _wait_for_events(events, 1)

    assert bridge.resolve(events[0].payload["approval_id"], "reject")
    result = await task

    assert isinstance(result, PermissionResultDeny)
    assert result.message == "User rejected this action"


@pytest.mark.asyncio
async def test_unknown_wallbit_tool_requires_approval() -> None:
    events: list[AgentEvent] = []
    bridge = UserInteractionBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(bridge.can_use_tool("mcp__wallbit__future_write", {"value": 1}))
    await _wait_for_events(events, 1)

    assert events[0].type == "approval_requested"
    assert bridge.resolve(events[0].payload["approval_id"], "reject")
    await task


@pytest.mark.asyncio
async def test_ask_user_question_emits_input_requested_and_allows_with_answer() -> None:
    events: list[AgentEvent] = []
    bridge = UserInteractionBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(
        bridge.can_use_tool(
            "AskUserQuestion",
            {
                "questions": [
                    {
                        "id": "currency",
                        "header": "Moneda",
                        "question": "¿En qué moneda?",
                        "options": [
                            {"label": "ARS", "description": "Pesos"},
                            {"label": "USD", "description": "Dólares"},
                        ],
                    }
                ]
            },
        )
    )
    await _wait_for_events(events, 1)

    input_request = events[0]
    assert input_request.type == "input_requested"
    assert input_request.payload["title"] == "Moneda"
    assert input_request.payload["question"] == "¿En qué moneda?"
    assert input_request.payload["options"] == [
        {"id": "ARS", "label": "ARS", "description": "Pesos"},
        {"id": "USD", "label": "USD", "description": "Dólares"},
    ]

    assert bridge.resolve_input(input_request.payload["input_id"], ["USD"])
    result = await task

    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input is not None
    assert result.updated_input["answers"] == {"¿En qué moneda?": "USD"}
    assert events[-1].type == "input_resolved"
    assert events[-1].payload["selected_options"] == ["USD"]


@pytest.mark.asyncio
async def test_ask_user_question_handles_multiple_questions() -> None:
    events: list[AgentEvent] = []
    bridge = UserInteractionBridge()
    bridge.set_event_sink(_collecting_sink(events))

    task = asyncio.create_task(
        bridge.can_use_tool(
            "AskUserQuestion",
            {
                "questions": [
                    {
                        "header": "Cantidad",
                        "question": "¿Qué cantidad?",
                        "options": [{"label": "USD 1000"}, {"label": "1000 acciones"}],
                    },
                    {
                        "header": "Orden",
                        "question": "¿Qué tipo de orden?",
                        "options": [{"label": "Mercado"}, {"label": "Límite"}],
                    },
                ]
            },
        )
    )

    await _wait_for_events(events, 1)
    assert events[0].type == "input_requested"
    assert bridge.resolve_input(events[0].payload["input_id"], ["USD 1000"])

    await _wait_for_events(events, 3)
    assert events[2].type == "input_requested"
    assert bridge.resolve_input(events[2].payload["input_id"], ["Mercado"])

    result = await task

    assert isinstance(result, PermissionResultAllow)
    assert result.updated_input is not None
    assert result.updated_input["answers"] == {
        "¿Qué cantidad?": "USD 1000",
        "¿Qué tipo de orden?": "Mercado",
    }


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
