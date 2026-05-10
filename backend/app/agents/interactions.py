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
    credential_requested_event,
    credential_resolved_event,
    input_requested_event,
    input_resolved_event,
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
    "get_checking_balance",
    "get_stocks_balance",
    "list_transactions",
    "get_asset",
    "mcp__wallbit__get_checking_balance",
    "mcp__wallbit__get_stocks_balance",
    "mcp__wallbit__list_transactions",
    "mcp__wallbit__get_asset",
    "mcp__wallbit__show_table",
}

WRITE_WALLBIT_TOOLS = {
    "create_trade",
    "mcp__wallbit__create_trade",
}

WRITE_DEFI_TOOLS = {
    "supply",
    "withdraw",
    "mcp__defi__supply",
    "mcp__defi__withdraw",
}

ApprovalResult = PermissionResultAllow | PermissionResultDeny
EventSink = Callable[[AgentEvent], Awaitable[None]]
ASK_USER_QUESTION_TOOL = "AskUserQuestion"
REQUEST_CREDENTIAL_TOOL_NAMES = {
    "request_credential",
    "mcp__ui__request_credential",
}


def requires_approval(tool_name: str) -> bool:
    if tool_name == ASK_USER_QUESTION_TOOL:
        return True
    if tool_name in REQUEST_CREDENTIAL_TOOL_NAMES:
        return True
    if tool_name in READ_WALLBIT_TOOLS:
        return False
    if tool_name in WRITE_WALLBIT_TOOLS:
        return True
    if tool_name in WRITE_DEFI_TOOLS:
        return True
    return tool_name.startswith("mcp__wallbit__")


class UserInteractionBridge:
    def __init__(self) -> None:
        self._event_sink: EventSink | None = None
        self._pending: dict[str, asyncio.Future[str]] = {}
        self._pending_inputs: dict[str, asyncio.Future[list[str]]] = {}
        self._pending_credentials: dict[str, asyncio.Future[str | None]] = {}

        self.handlers = {
            ASK_USER_QUESTION_TOOL: self._handle_ask_user_question,
            "request_credential": self._handle_request_credential,
            "mcp__ui__request_credential": self._handle_request_credential,
        }

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
        if handler := self.handlers.get(tool_name):
            return await handler(input_data, options)

        if not requires_approval(tool_name):
            return PermissionResultAllow(updated_input=input_data)

        return await self._handle_security_approval(tool_name, input_data)

    async def _handle_security_approval(
        self,
        tool_name: str,
        input_data: dict[str, Any]
    ) -> ApprovalResult:
        if self._event_sink is None:
            return PermissionResultDeny(message="No approval channel is available for this action.")

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

    def resolve_input(self, input_id: str, selected_options: list[str] | str) -> bool:
        if isinstance(selected_options, str):
            normalized = [selected_options]
        else:
            normalized = selected_options

        future = self._pending_inputs.get(input_id)
        if future is None or future.done():
            return False
        future.set_result(normalized)
        return True

    def resolve_credential(self, request_id: str, value: str | None) -> bool:
        """Set the result for a pending credential request.

        `value` is the user-entered text on submit, or `None` if cancelled.
        """
        future = self._pending_credentials.get(request_id)
        if future is None or future.done():
            return False
        future.set_result(value)
        return True

    async def _handle_request_credential(
        self,
        input_data: dict[str, Any],
        options: dict[str, Any] | None,
    ) -> ApprovalResult:
        del options

        if self._event_sink is None:
            import structlog
            structlog.get_logger(__name__).error("request_credential_failed_no_sink_WTF")
            return PermissionResultDeny(
                message="No credential channel is available.",
            )

        request_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future: asyncio.Future[str | None] = loop.create_future()
        self._pending_credentials[request_id] = future

        title = str(input_data.get("title") or input_data.get("label") or "Dato sensible")
        instructions = str(
            input_data.get("instructions")
            or input_data.get("question")
            or "Pegá el dato y confirmá."
        )
        kind = str(input_data.get("kind") or "secret")
        placeholder = input_data.get("placeholder")

        await self._event_sink(
            credential_requested_event(
                request_id=request_id,
                title=title,
                instructions=instructions,
                kind=kind,
                placeholder=str(placeholder) if isinstance(placeholder, str) else None,
            )
        )

        try:
            value = await future
        finally:
            self._pending_credentials.pop(request_id, None)

        await self._event_sink(
            credential_resolved_event(request_id=request_id, cancelled=value is None)
        )

        if value is None:
            return PermissionResultDeny(message="User cancelled credential entry")

        return PermissionResultAllow(
            updated_input={"value": value, "kind": kind},
        )

    async def _handle_ask_user_question(
        self,
        input_data: dict[str, Any],
        options: dict[str, Any] | None,
    ) -> ApprovalResult:
        del options

        if self._event_sink is None:
            return PermissionResultDeny(
                message="No user input channel is available for this question."
            )

        answers: dict[str, str | list[str]] = {}
        for question in _questions(input_data):
            input_id = uuid.uuid4().hex
            loop = asyncio.get_running_loop()
            future: asyncio.Future[list[str]] = loop.create_future()
            self._pending_inputs[input_id] = future

            normalized_options = _question_options(question)
            multi_select = _question_multi_select(question)
            question_text = _question_text(question)
            await self._event_sink(
                input_requested_event(
                    input_id=input_id,
                    title=_question_title(question),
                    question=question_text,
                    options=normalized_options,
                    multi_select=multi_select,
                )
            )

            try:
                selected_options = await future
            finally:
                self._pending_inputs.pop(input_id, None)

            selected_labels = _selected_labels(normalized_options, selected_options)
            await self._event_sink(
                input_resolved_event(
                    input_id=input_id,
                    selected_options=selected_labels,
                )
            )
            answers[question_text] = selected_labels if multi_select else selected_labels[0]

        return PermissionResultAllow(
            updated_input={
                "questions": input_data.get("questions", []),
                "answers": answers,
            }
        )


def _questions(input_data: dict[str, Any]) -> list[dict[str, Any]]:
    questions = input_data.get("questions")
    if isinstance(questions, list):
        normalized = [question for question in questions if isinstance(question, dict)]
        if normalized:
            return normalized
    return [input_data]


def _question_title(question: dict[str, Any]) -> str:
    raw = question.get("header") or question.get("title") or "Elegir opcion"
    return str(raw)


def _question_text(question: dict[str, Any]) -> str:
    raw = question.get("question") or question.get("prompt") or _question_title(question)
    return str(raw)


def _question_multi_select(question: dict[str, Any]) -> bool:
    return bool(question.get("multiSelect") or question.get("multi_select"))


def _question_options(question: dict[str, Any]) -> list[dict[str, str]]:
    raw_options = question.get("options")
    if not isinstance(raw_options, list):
        return []

    normalized: list[dict[str, str]] = []
    for index, option in enumerate(raw_options, start=1):
        if isinstance(option, str):
            normalized.append({"id": option, "label": option, "description": ""})
            continue

        if not isinstance(option, dict):
            label = str(option)
            normalized.append({"id": label, "label": label, "description": ""})
            continue

        label = str(option.get("label") or option.get("value") or option.get("id") or index)
        option_id = str(option.get("id") or option.get("value") or label)
        description = str(option.get("description") or "")
        normalized.append({"id": option_id, "label": label, "description": description})

    return normalized


def _selected_labels(
    options: list[dict[str, str]],
    selected_options: list[str],
) -> list[str]:
    labels_by_id = {option["id"]: option["label"] for option in options}
    labels_by_label = {option["label"]: option["label"] for option in options}
    return [
        labels_by_id.get(selected, labels_by_label.get(selected, selected))
        for selected in selected_options
    ]
