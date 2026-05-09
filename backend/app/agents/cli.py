from __future__ import annotations

import asyncio
import json
from typing import Any

from app.agents.chat_agent import ChatAgentSession
from app.agents.events import AgentEvent

CONFIRM_INPUTS = {"confirm", "c", "y", "yes"}
REJECT_INPUTS = {"reject", "r", "n", "no"}
CONNECT_TIMEOUT_SECONDS = 30


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

            print("OpenFi> ", end="", flush=True)
            printed_tokens = False
            async for event in session.send_user_message(user_text):
                printed_tokens = _render_event(event, session, printed_tokens)
            print()
    finally:
        await session.disconnect()
        print("Disconnected.")


def _render_event(
    event: AgentEvent,
    session: ChatAgentSession,
    printed_tokens: bool = False,
) -> bool:
    if event.type == "agent_token":
        print(event.payload["text"], end="", flush=True)
        return True

    if event.type == "agent_message":
        text = event.payload.get("text")
        if text and not printed_tokens:
            print(text, end="", flush=True)
            return True
        if text:
            print()
        return printed_tokens

    if event.type == "tool_call_started":
        print(
            f"\n[tool:start] {event.payload.get('tool_name')} "
            f"{event.payload.get('input_summary')}"
        )
        return printed_tokens

    if event.type == "tool_call_finished":
        status = "error" if event.payload.get("is_error") else "ok"
        print(f"\n[tool:{status}] {event.payload.get('result_summary')}")
        return printed_tokens

    if event.type == "approval_requested":
        _handle_approval(event, session)
        return printed_tokens

    if event.type == "approval_resolved":
        print(f"\n[approval] {event.payload.get('decision')}")
        return printed_tokens

    if event.type == "session_status":
        print(f"\n[status] {_json(event.to_dict())}")
        return printed_tokens

    if event.type == "error":
        print(f"\n[error] {event.payload.get('message')}")
        if event.payload.get("details") is not None:
            print(f"[error:details] {event.payload['details']}")
        return printed_tokens

    print(f"\n[event] {_json(event.to_dict())}")
    return printed_tokens


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


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    asyncio.run(main())
