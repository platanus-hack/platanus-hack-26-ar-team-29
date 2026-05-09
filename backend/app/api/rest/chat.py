"""REST routes for chat sessions + messages."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.api.deps import get_chat_service, get_current_user_id
from app.common.errors import NOT_FOUND, APIError
from app.services.chat import ChatService

router = APIRouter()


class CreateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class ResolveInputRequest(BaseModel):
    selected_options: list[str] | str = Field(...)


@router.post("/sessions")
async def create_session(
    body: CreateSessionRequest | None = None,
    user_id: UUID = Depends(get_current_user_id),
    svc: ChatService = Depends(get_chat_service),
) -> dict:
    title = body.title if body else None
    return await svc.create_session(user_id=user_id, title=title)


@router.get("/sessions")
async def list_sessions(
    user_id: UUID = Depends(get_current_user_id),
    svc: ChatService = Depends(get_chat_service),
) -> list[dict]:
    return await svc.list_sessions(user_id=user_id)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    svc: ChatService = Depends(get_chat_service),
) -> JSONResponse:
    await svc.delete_session(user_id=user_id, session_id=session_id)
    return JSONResponse(status_code=204, content=None)


@router.get("/sessions/{session_id}/messages")
async def list_messages(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    svc: ChatService = Depends(get_chat_service),
) -> list[dict]:
    return await svc.list_messages(user_id=user_id, session_id=session_id)


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: UUID,
    body: SendMessageRequest,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    svc: ChatService = Depends(get_chat_service),
) -> JSONResponse:
    agent_tasks = request.app.state.agent_tasks
    payload = await svc.send_user_message(
        user_id=user_id,
        session_id=session_id,
        content=body.content,
        agent_tasks=agent_tasks,
    )
    return JSONResponse(status_code=202, content=payload)


@router.post("/sessions/{session_id}/inputs/{input_id}/resolve")
async def resolve_input(
    session_id: UUID,
    input_id: str,
    body: ResolveInputRequest,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),  # noqa: ARG001 - dev auth gate
) -> dict:
    chat_agent = request.app.state.chat_agent
    agent_session = chat_agent.get_session(session_id)
    resolved = agent_session.resolve_input(input_id, body.selected_options)
    if not resolved:
        raise APIError(
            NOT_FOUND,
            http_status=404,
            message_es="No hay una pregunta pendiente con ese identificador.",
            message_en="No pending input with that id.",
        )
    return {"ok": True, "input_id": input_id}
