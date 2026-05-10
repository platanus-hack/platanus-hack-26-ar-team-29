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

    from app.workers.poller import global_poll_loop

    poller_task = asyncio.create_task(global_poll_loop())
    agent_tasks.add(poller_task)

    app.state.connection_manager = connection_manager
    app.state.provider_registry = provider_registry
    app.state.wallbit_provider = wallbit_provider
    app.state.ethereum_provider = ethereum_provider
    app.state.chat_agent = chat_agent
    app.state.wallbit_base_url = settings.wallbit_base_url
    app.state.agent_tasks = agent_tasks

    # Seed a Wallbit connection for the dev user using the env API key so the
    # Connections page shows it as already linked. Idempotent: skips if any
    # active wallbit connection already exists for the user.
    if settings.wallbit_api_key:
        try:
            from app.api.deps import DEV_USER_ID
            from app.persistence.repositories.connections import ConnectionRepository
            from app.persistence.session import session_factory
            from app.providers.wallbit.auth import WallbitCredentials

            async with session_factory() as db:
                repo = ConnectionRepository(db)
                existing = await repo.get_active_wallbit(DEV_USER_ID)
                if existing is None:
                    creds = WallbitCredentials(api_key=settings.wallbit_api_key)
                    await repo.create_wallbit(
                        user_id=DEV_USER_ID,
                        label="Wallbit",
                        credentials_encrypted=creds.to_blob(),
                        capabilities=["read_balance", "read_transactions", "place_trade"],
                        metadata={},
                    )
                    await db.commit()
                    log.info("wallbit_dev_connection_seeded", user_id=str(DEV_USER_ID))
        except Exception as exc:  # noqa: BLE001 — startup seed must never block boot.
            log.warning("wallbit_dev_seed_failed", error=str(exc))

    log.info("app_startup", env=settings.env)
    try:
        yield
    finally:
        # Cancel agent tasks gracefully.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        my_tasks = [t for t in agent_tasks if t.get_loop() is loop] if loop else list(agent_tasks)

        for task in my_tasks:
            task.cancel()
        if my_tasks:
            await asyncio.gather(*my_tasks, return_exceptions=True)

        for task in my_tasks:
            agent_tasks.discard(task)

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
