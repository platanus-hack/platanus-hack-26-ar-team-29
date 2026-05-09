from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from app.agents.chat_agent import ChatAgentSession
from app.agents.events import AgentEvent

CONFIRM_INPUTS = {"confirm", "c", "y", "yes"}
REJECT_INPUTS = {"reject", "r", "n", "no"}
CONNECT_TIMEOUT_SECONDS = 30


@dataclass
class RenderState:
    printed_tokens: bool = False
    saw_visible_event: bool = False
    hidden_tool_ids: set[str] = field(default_factory=set)


async def main() -> None:
    session = ChatAgentSession()
    print("OpenFi live chat. Type /exit to quit, /status for MCP status.", flush=True)
    print("Connecting to Claude Agent SDK...", flush=True)

    try:
        await asyncio.wait_for(session.connect(), timeout=CONNECT_TIMEOUT_SECONDS)
        print("Connected.", flush=True)
    except TimeoutError:
        print(
            "Could not connect: Claude Agent SDK startup timed out. "
            "Check Claude Code authentication and network/MCP access.",
            flush=True,
        )
        return
    except Exception as exc:  # noqa: BLE001 - CLI should show startup failures.
        print(f"Could not connect: {exc}", flush=True)
        return

    try:
        while True:
            user_text = await asyncio.to_thread(input, "\nYou> ")
            command = user_text.strip()

            if command == "/exit":
                break
            if command == "/status":
                _render_event(await session.get_status(), session)
                continue
            if command == "/interrupt":
                _render_event(await session.interrupt(), session)
                continue
            if not command:
                continue

            print("Pampa> ", end="", flush=True)
            render_state = RenderState()
            async for event in session.send_user_message(user_text):
                _render_event(event, session, render_state)
            if not render_state.saw_visible_event:
                print(
                    "\n[turno terminado sin respuesta visible; probá seguir con otro mensaje]",
                    end="",
                )
            print()
    finally:
        await session.disconnect()
        print("Disconnected.")


def _render_event(
    event: AgentEvent,
    session: ChatAgentSession,
    render_state: RenderState | None = None,
) -> None:
    state = render_state or RenderState()
    if event.type == "agent_token":
        print(event.payload["text"], end="", flush=True)
        state.printed_tokens = True
        state.saw_visible_event = True
        return

    if event.type == "agent_message":
        text = event.payload.get("text")
        if text and not state.printed_tokens:
            print(text, end="", flush=True)
            state.printed_tokens = True
            state.saw_visible_event = True
            return
        if text:
            print()
            state.saw_visible_event = True
        return

    if event.type == "tool_call_started":
        if event.payload.get("tool_name") == "AskUserQuestion":
            tool_use_id = event.payload.get("tool_use_id")
            if tool_use_id:
                state.hidden_tool_ids.add(str(tool_use_id))
            return
        print(
            f"\n[tool:start] {event.payload.get('tool_name')} "
            f"{event.payload.get('input_summary')}"
        )
        state.saw_visible_event = True
        return

    if event.type == "tool_call_finished":
        tool_use_id = event.payload.get("tool_use_id")
        if tool_use_id and str(tool_use_id) in state.hidden_tool_ids:
            return
        status = "error" if event.payload.get("is_error") else "ok"
        print(f"\n[tool:{status}] {event.payload.get('result_summary')}")
        state.saw_visible_event = True
        return

    if event.type == "approval_requested":
        _handle_approval(event, session)
        state.saw_visible_event = True
        return

    if event.type == "input_requested":
        _handle_input(event, session)
        state.saw_visible_event = True
        return

    if event.type == "input_resolved":
        print(f"\n[input] {', '.join(event.payload.get('selected_options', []))}")
        state.saw_visible_event = True
        return

    if event.type == "approval_resolved":
        print(f"\n[approval] {event.payload.get('decision')}")
        state.saw_visible_event = True
        return

    if event.type == "session_status":
        print(f"\n[status] {_json(event.to_dict())}")
        state.saw_visible_event = True
        return

    if event.type == "error":
        print(f"\n[error] {event.payload.get('message')}")
        if event.payload.get("details") is not None:
            print(f"[error:details] {event.payload['details']}")
        state.saw_visible_event = True
        return

    print(f"\n[event] {_json(event.to_dict())}")
    state.saw_visible_event = True


def _handle_approval(event: AgentEvent, session: ChatAgentSession) -> None:
    approval_id = event.payload["approval_id"]
    print("\n[approval required]")
    print(event.payload["title"])
    print(event.payload["message"])
    print(f"tool: {event.payload['tool_name']}")
    print(f"input: {_json(event.payload.get('input'))}")

    while True:
        answer = input("confirm/reject> ").strip().lower()
        if answer in CONFIRM_INPUTS:
            decision = "confirm"
            break
        if answer in REJECT_INPUTS:
            decision = "reject"
            break
        print("Please type confirm or reject.")

    if not session.resolve_approval(approval_id, decision):
        print("[approval] request already resolved or expired")


def _handle_input(event: AgentEvent, session: ChatAgentSession) -> None:
    input_id = event.payload["input_id"]
    options = event.payload.get("options", [])

    print()
    title = event.payload.get("title")
    if title:
        print(title)
    print(event.payload.get("question", "Elegí una opción"))

    for index, option in enumerate(options, start=1):
        label = option.get("label") or option.get("id") or str(index)
        description = option.get("description")
        suffix = f" - {description}" if description else ""
        print(f"[{index}] {label}{suffix}")

    selected = _read_option_selection(options, bool(event.payload.get("multi_select")))
    if not session.resolve_input(input_id, selected):
        print("[input] request already resolved or expired")


def _read_option_selection(
    options: list[dict[str, Any]],
    multi_select: bool,
) -> list[str]:
    while True:
        prompt = "Elegí una o más (coma separado)> " if multi_select else "Elegí> "
        answer = input(prompt).strip()
        if not answer:
            continue

        raw_choices = [part.strip() for part in answer.split(",")] if multi_select else [answer]
        selected_values: list[str] = []
        failed = False
        for raw_choice in raw_choices:
            selected = _match_option(raw_choice, options)
            if selected is None:
                failed = True
                break
            selected_values.append(str(selected.get("id") or selected.get("label") or raw_choice))

        if not failed:
            return selected_values

        print("Opción inválida. Elegí por número o por nombre.")


def _match_option(answer: str, options: list[dict[str, Any]]) -> dict[str, Any] | None:
    if answer.isdigit():
        index = int(answer)
        if 1 <= index <= len(options):
            return options[index - 1]

    for option in options:
        option_id = str(option.get("id") or "")
        label = str(option.get("label") or "")
        if answer.lower() in {option_id.lower(), label.lower()}:
            return option

    return None


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    asyncio.run(main())
