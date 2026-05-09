from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agents.chat_agent import normalize_sdk_message


@dataclass
class TextDelta:
    text: str


@dataclass
class StreamEvent:
    type: str
    delta: Any | None = None
    content_block: Any | None = None


@dataclass
class TextBlock:
    text: str


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]


@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: Any
    is_error: bool = False


@dataclass
class AssistantMessage:
    content: list[Any]


def test_stream_text_delta_becomes_agent_token() -> None:
    events = normalize_sdk_message(
        StreamEvent(type="content_block_delta", delta=TextDelta("hola"))
    )

    assert [event.to_dict() for event in events] == [
        {"type": "agent_token", "text": "hola"}
    ]


def test_stream_tool_start_becomes_tool_call_started() -> None:
    events = normalize_sdk_message(
        StreamEvent(
            type="content_block_start",
            content_block=ToolUseBlock(
                id="toolu_1",
                name="mcp__wallbit__get_asset",
                input={"symbol": "SPY"},
            ),
        )
    )

    assert events[0].type == "tool_call_started"
    assert events[0].payload["tool_use_id"] == "toolu_1"
    assert events[0].payload["tool_name"] == "mcp__wallbit__get_asset"


def test_completed_message_becomes_agent_message_and_tool_events() -> None:
    events = normalize_sdk_message(
        AssistantMessage(
            content=[
                TextBlock("Listo."),
                ToolUseBlock(
                    id="toolu_1",
                    name="mcp__wallbit__get_asset",
                    input={"symbol": "SPY"},
                ),
                ToolResultBlock(tool_use_id="toolu_1", content={"ok": True}),
            ]
        )
    )

    assert [event.type for event in events] == [
        "tool_call_started",
        "tool_call_finished",
        "agent_message",
    ]
    assert events[-1].payload["text"] == "Listo."
