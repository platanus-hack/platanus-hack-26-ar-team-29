"""FastAPI dependencies — auth (dev user only) + service factories."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.session import get_session

if TYPE_CHECKING:
    from app.api.ws.manager import ConnectionManager
    from app.services.chat import ChatService
    from app.services.connections import ConnectionService
    from app.services.onchain import OnchainService
    from app.services.plans import PlanService
    from app.services.portfolio import PortfolioService


DEV_USER_ID: UUID = UUID("00000000-0000-0000-0000-000000000001")


def get_current_user_id() -> UUID:
    return DEV_USER_ID


def get_chat_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> ChatService:
    from app.services.chat import ChatService

    return ChatService(
        session=session,
        manager=request.app.state.connection_manager,
        agent=request.app.state.chat_agent,
    )


def get_plan_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> PlanService:
    from app.services.plans import PlanService

    return PlanService(
        session=session,
        manager=request.app.state.connection_manager,
        agent=request.app.state.chat_agent,
    )


def get_connection_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> ConnectionService:
    from app.services.connections import ConnectionService

    return ConnectionService(
        session=session,
        wallbit_base_url=request.app.state.wallbit_base_url,
    )


def get_portfolio_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> PortfolioService:
    from app.services.portfolio import PortfolioService

    return PortfolioService(
        session=session,
        wallbit_base_url=request.app.state.wallbit_base_url,
    )


def get_connection_manager(request: Request) -> ConnectionManager:
    return request.app.state.connection_manager


def get_onchain_service(
    session: AsyncSession = Depends(get_session),
    request: Request = None,  # type: ignore[assignment]
) -> OnchainService:
    from app.services.connections import ConnectionService
    from app.services.onchain import OnchainService

    eth_provider = request.app.state.ethereum_provider
    return OnchainService(
        session=session,
        connection_service=ConnectionService(
            session=session,
            wallbit_base_url=request.app.state.wallbit_base_url,
        ),
        eth_client=eth_provider.client,
    )
