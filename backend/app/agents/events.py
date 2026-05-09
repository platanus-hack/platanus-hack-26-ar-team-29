from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ChatAction:
    id: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": self.label}


@dataclass(frozen=True)
class AgentEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **self.payload}


def summarize_value(value: Any, *, max_chars: int = 600) -> str:
    try:
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        rendered = repr(value)

    if len(rendered) <= max_chars:
        return rendered
    return f"{rendered[: max_chars - 3]}..."


def approval_requested_event(
    *,
    approval_id: str,
    tool_name: str,
    input_data: dict[str, Any],
) -> AgentEvent:
    return AgentEvent(
        "approval_requested",
        {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "title": "Confirmar operacion",
            "message": "OpenFi quiere ejecutar esta operacion en Wallbit.",
            "input": input_data,
            "actions": [
                ChatAction("confirm", "Confirm").to_dict(),
                ChatAction("reject", "Reject").to_dict(),
            ],
        },
    )


def input_requested_event(
    *,
    input_id: str,
    title: str,
    question: str,
    options: list[dict[str, str]],
    multi_select: bool,
) -> AgentEvent:
    return AgentEvent(
        "input_requested",
        {
            "input_id": input_id,
            "title": title,
            "question": question,
            "options": options,
            "multi_select": multi_select,
        },
    )


def input_resolved_event(
    *,
    input_id: str,
    selected_options: list[str],
) -> AgentEvent:
    return AgentEvent(
        "input_resolved",
        {
            "input_id": input_id,
            "selected_options": selected_options,
        },
    )


def approval_resolved_event(
    *,
    approval_id: str,
    tool_name: str,
    decision: str,
) -> AgentEvent:
    return AgentEvent(
        "approval_resolved",
        {
            "approval_id": approval_id,
            "tool_name": tool_name,
            "decision": decision,
        },
    )


def error_event(message: str, *, details: Any | None = None) -> AgentEvent:
    payload: dict[str, Any] = {"message": message}
    if details is not None:
        payload["details"] = details
    return AgentEvent("error", payload)
