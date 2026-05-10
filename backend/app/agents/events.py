from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

TOOL_LABELS = {
    "get_checking_balance": "Get Checking Balance",
    "get_stocks_balance": "Get Stocks Balance",
    "list_transactions": "List Transactions",
    "get_asset": "Get Asset Info",
    "create_trade": "Create Trade",
    "AskUserQuestion": "Ask Question",
    "mcp__wallbit__get_checking_balance": "Get Checking Balance",
    "mcp__wallbit__get_stocks_balance": "Get Stocks Balance",
    "mcp__wallbit__list_transactions": "List Transactions",
    "mcp__wallbit__get_asset": "Get Asset Info",
    "mcp__wallbit__create_trade": "Create Trade",
}


def format_tool_name(tool_name: str | None) -> str:
    """Returns the human-readable name of the tool, or attempts to format it if not found."""
    if not tool_name:
        return "Unknown Tool"

    if tool_name in TOOL_LABELS:
        return TOOL_LABELS[tool_name]

    # Fallback: remove mcp__ prefixes and format snake_case to Title Case
    clean_name = tool_name.replace("mcp__wallbit__", "").replace("mcp__", "")
    return clean_name.replace("_", " ").title()


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


def credential_requested_event(
    *,
    request_id: str,
    title: str,
    instructions: str,
    kind: str,
    placeholder: str | None = None,
) -> AgentEvent:
    return AgentEvent(
        "credential_requested",
        {
            "request_id": request_id,
            "title": title,
            "instructions": instructions,
            "kind": kind,
            "placeholder": placeholder,
        },
    )


def credential_resolved_event(
    *,
    request_id: str,
    cancelled: bool = False,
) -> AgentEvent:
    return AgentEvent(
        "credential_resolved",
        {"request_id": request_id, "cancelled": cancelled},
    )


def error_event(message: str, *, details: Any | None = None) -> AgentEvent:
    payload: dict[str, Any] = {"message": message}
    if details is not None:
        payload["details"] = details
    return AgentEvent("error", payload)
