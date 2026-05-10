import asyncio

import structlog
from sqlalchemy import select

from app.config import get_settings
from app.persistence.models.connections import ProviderConnection
from app.persistence.session import session_factory
from app.workers.classifier_worker import process_unclassified
from app.workers.context_worker import main as process_dirty_profiles

log = structlog.get_logger(__name__)


async def global_poll_loop():
    settings = get_settings()
    interval = settings.poll_interval_seconds

    # Wait a few seconds before starting the first poll to let the app initialize completely
    await asyncio.sleep(5)

    while True:
        try:
            log.info("starting_global_poll")
            # 1. Sync all wallbit connections (page 1 is enough for periodic polling, but we can do sync_all for safety)
            # Or better yet, we just sync page 1 if we have a routine sync, but we use the sync_all for MVP.
            # Actually, for polling, we can just use the page 1 sync to be faster and not hit API limits.
            from app.services.ingestion import sync_wallbit_transactions

            async with session_factory() as session:
                stmt = select(ProviderConnection).where(
                    ProviderConnection.connection_type == "wallbit"
                )
                conns = (await session.execute(stmt)).scalars().all()

                for conn in conns:
                    try:
                        await sync_wallbit_transactions(session, conn.id)
                    except Exception as e:
                        log.error("wallbit_sync_error", conn_id=str(conn.id), error=str(e))

            # 2. Classify unclassified
            await process_unclassified()

            # 3. Recalculate contexts
            await process_dirty_profiles()

            log.info("global_poll_complete", next_run_in=interval)
        except Exception as e:
            log.error("global_poll_error", error=str(e))

        await asyncio.sleep(interval)
