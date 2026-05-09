from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.common.errors import register_error_handlers
from app.common.logging import setup_logging
from app.config import get_settings
from app.persistence import crypto

log = structlog.get_logger(__name__)


# Module-level strong-reference set so spawned tasks survive GC.
agent_tasks: set[asyncio.Task] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    settings = get_settings()

    # Fail fast if FERNET_KEY is missing/garbled.
    crypto.encrypt(b"_")

    from app.agents.chat_agent import ChatAgent
    from app.agents.plan_executor import PlanExecutor
    from app.agents.tool_dispatcher import ToolDispatcher
    from app.ai.anthropic import AnthropicClient
    from app.api.ws.manager import ConnectionManager
    from app.providers.registry import ProviderRegistry
    from app.providers.wallbit.capabilities import WallbitProvider

    connection_manager = ConnectionManager()
    provider_registry = ProviderRegistry()
    wallbit_provider = WallbitProvider(base_url=settings.wallbit_base_url)
    provider_registry.register(wallbit_provider)

    anthropic_client = AnthropicClient(
        api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
    )
    dispatcher = ToolDispatcher()

    chat_agent = ChatAgent(
        anthropic=anthropic_client,
        dispatcher=dispatcher,
        manager=connection_manager,
        agent_tasks=agent_tasks,
    )
    plan_executor = PlanExecutor(
        wallbit_provider=wallbit_provider,
        manager=connection_manager,
        agent_tasks=agent_tasks,
    )

    # Tool registrations (read tools dispatched by the agent).
    from app.agents import bootstrap_tools

    bootstrap_tools(dispatcher)

    app.state.connection_manager = connection_manager
    app.state.provider_registry = provider_registry
    app.state.wallbit_provider = wallbit_provider
    app.state.anthropic_client = anthropic_client
    app.state.dispatcher = dispatcher
    app.state.chat_agent = chat_agent
    app.state.plan_executor = plan_executor
    app.state.wallbit_base_url = settings.wallbit_base_url
    app.state.agent_tasks = agent_tasks

    log.info("app_startup", env=settings.env)
    try:
        yield
    finally:
        # Cancel agent tasks gracefully.
        for task in list(agent_tasks):
            task.cancel()
        if agent_tasks:
            await asyncio.gather(*agent_tasks, return_exceptions=True)
        agent_tasks.clear()
        await wallbit_provider.aclose()
        from app.persistence.session import reset_engine

        await reset_engine()
        log.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level, settings.env)

    app = FastAPI(title="Pampa Backend", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
