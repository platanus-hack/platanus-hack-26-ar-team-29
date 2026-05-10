"""FastAPI dependencies — auth + service factories."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.anthropic import AnthropicClient
from app.api.ws.manager import ConnectionManager
from app.common.errors import UNAUTHORIZED, APIError
from app.config import get_settings
from app.persistence.session import get_session
from app.services.chat import ChatService
from app.services.connections import ConnectionService
from app.services.defi import DefiService
from app.services.onchain import OnchainService
from app.services.plans import PlanService
from app.services.portfolio import PortfolioService
from app.services.profiler import ProfilerService

DEV_USER_ID: UUID = UUID("00000000-0000-0000-0000-000000000001")
DEV_TOKEN_PREFIX = "dev-"


def parse_dev_user_token(token: str | None) -> UUID:
    if not token or not token.startswith(DEV_TOKEN_PREFIX):
        raise APIError(
            UNAUTHORIZED,
            http_status=401,
            message_es="Falta un token de autenticación válido.",
            message_en="Missing valid authentication token.",
        )
    raw_user_id = token[len(DEV_TOKEN_PREFIX) :].strip()
    try:
        return UUID(raw_user_id)
    except ValueError as exc:
        raise APIError(
            UNAUTHORIZED,
            http_status=401,
            message_es="El token de autenticación no es válido.",
            message_en="Invalid authentication token.",
        ) from exc


def user_id_from_authorization(authorization: str | None) -> UUID:
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise APIError(
            UNAUTHORIZED,
            http_status=401,
            message_es="Falta un token Bearer válido.",
            message_en="Missing valid Bearer token.",
        )
    return parse_dev_user_token(token)


def get_current_user_id(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> UUID:
    return user_id_from_authorization(authorization)


def get_chat_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> ChatService:

    return ChatService(
        session=session,
        manager=request.app.state.connection_manager,
        agent=request.app.state.chat_agent,
    )


def get_plan_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> PlanService:

    return PlanService(
        session=session,
        manager=request.app.state.connection_manager,
        agent=request.app.state.chat_agent,
    )


def get_connection_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> ConnectionService:

    return ConnectionService(
        session=session,
        wallbit_base_url=request.app.state.wallbit_base_url,
    )


def get_portfolio_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> PortfolioService:

    eth_provider = request.app.state.ethereum_provider
    return PortfolioService(
        session=session,
        wallbit_base_url=request.app.state.wallbit_base_url,
        eth_client=eth_provider.client,
    )


def get_profiler_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> ProfilerService:

    settings = get_settings()
    eth_provider = request.app.state.ethereum_provider

    return ProfilerService(
        session=session,
        portfolio_service=PortfolioService(
            session=session,
            wallbit_base_url=request.app.state.wallbit_base_url,
            eth_client=eth_provider.client,
        ),
        anthropic_client=AnthropicClient(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        ),
    )


def get_connection_manager(request: Request) -> ConnectionManager:
    return request.app.state.connection_manager


def get_onchain_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> OnchainService:

    eth_provider = request.app.state.ethereum_provider
    return OnchainService(
        session=session,
        connection_service=ConnectionService(
            session=session,
            wallbit_base_url=request.app.state.wallbit_base_url,
        ),
        eth_client=eth_provider.client,
    )


def get_defi_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> DefiService:

    eth_provider = request.app.state.ethereum_provider
    return DefiService(
        session=session,
        connection_service=ConnectionService(
            session=session,
            wallbit_base_url=request.app.state.wallbit_base_url,
        ),
        eth_client=eth_provider.client,
    )
