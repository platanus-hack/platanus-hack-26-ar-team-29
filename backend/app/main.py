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
    from app.api.ws.manager import ConnectionManager
    from app.providers.ethereum.capabilities import EthereumCustodialProvider
    from app.providers.registry import ProviderRegistry
    from app.providers.wallbit.capabilities import WallbitProvider

    connection_manager = ConnectionManager()
    provider_registry = ProviderRegistry()
    wallbit_provider = WallbitProvider(base_url=settings.wallbit_base_url)
    ethereum_provider = EthereumCustodialProvider(rpc_urls=settings.ethereum_rpc_urls)
    provider_registry.register(wallbit_provider)
    provider_registry.register(ethereum_provider)


    chat_agent = ChatAgent(
        manager=connection_manager,
        agent_tasks=agent_tasks,
    )


    app.state.connection_manager = connection_manager
    app.state.provider_registry = provider_registry
    app.state.wallbit_provider = wallbit_provider
    app.state.ethereum_provider = ethereum_provider
    app.state.chat_agent = chat_agent
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

    app = FastAPI(title="OpenFi Backend", version="0.1.0", lifespan=lifespan)

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
