import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.classifier_agent import classify_transactions
from app.config import get_settings
from app.persistence.crypto import decrypt
from app.persistence.models.connections import ProviderConnection
from app.persistence.models.ledger import CanonicalTransaction
from app.persistence.models.users import UserProfile
from app.persistence.session import session_factory
from app.providers.wallbit.client import WallbitClient
from app.services.context import recalculate_user_profile


import structlog

log = structlog.get_logger(__name__)


async def _upsert_wallbit_txs(
    session: AsyncSession, conn: ProviderConnection, raw_txs: list[dict[str, Any]]
) -> int:
    inserted_or_updated = 0
    for raw in raw_txs:
        # Normalize
        external_id = raw.get("uuid")
        status = raw.get("status", "completed").lower()
        if status not in ("completed", "pending", "failed", "cancelled"):
            status = "completed"

        raw_type = raw.get("type", "")
        if raw_type == "TRADE":
            ctype = "trade"
        elif raw_type in ("INVESTMENT_DEPOSIT", "INVESTMENT_WITHDRAWAL"):
            ctype = "transfer_internal"
        else:
            ctype = "other"

        raw_date = raw.get("created_at", "").replace("Z", "+00:00")
        occurred_at = datetime.fromisoformat(raw_date)

        source_amount = raw.get("source_amount")
        source_currency = raw.get("source_currency", {}).get("code")
        dest_amount = raw.get("dest_amount")
        dest_unit = raw.get("dest_currency", {}).get("code")

        fee_amount = 0.0
        fee_currency = None
        if "fee" in raw and raw["fee"]:
            fee_amount = raw["fee"].get("fee_amount", 0.0)
            fee_currency = raw["fee"].get("fee_currency")

        trade_info = raw.get("trade_info", {})
        direction = None
        if ctype == "trade" and trade_info:
            dir_raw = trade_info.get("direction", "").lower()
            direction = "out" if dir_raw == "buy" else "in"

        merchant = trade_info.get("symbol") if ctype == "trade" else None

        # Upsert
        stmt = insert(CanonicalTransaction).values(
            user_id=conn.user_id,
            connection_id=conn.id,
            external_id=external_id,
            type=ctype,
            direction=direction,
            source_amount=source_amount,
            source_currency=source_currency,
            dest_amount=dest_amount,
            dest_unit=dest_unit,
            fee_amount=fee_amount,
            fee_currency=fee_currency,
            status=status,
            occurred_at=occurred_at,
            raw_provider_payload=raw,
            source_kind="provider_pulled",
            merchant=merchant,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["connection_id", "external_id"],
            set_=dict(
                status=stmt.excluded.status,
                raw_provider_payload=stmt.excluded.raw_provider_payload,
            ),
        )

        await session.execute(stmt)
        inserted_or_updated += 1
    return inserted_or_updated


async def sync_wallbit_transactions(session: AsyncSession, connection_id: uuid.UUID) -> int:
    """Fetch Wallbit transactions for a connection and upsert into CanonicalTransaction."""
    stmt = select(ProviderConnection).where(ProviderConnection.id == connection_id)
    result = await session.execute(stmt)
    conn = result.scalar_one_or_none()

    if not conn or conn.connection_type != "wallbit":
        return 0

    creds_json = decrypt(conn.credentials_encrypted).decode("utf-8")

    creds = json.loads(creds_json)
    api_key = creds.get("api_key")
    if not api_key:
        return 0

    settings = get_settings()
    url = settings.wallbit_base_url

    inserted_or_updated = 0
    async with WallbitClient(api_key=api_key, base_url=url) as client:
        try:
            # We'll just fetch page 1 for the MVP
            data = await client._request("GET", "/transactions")
            raw_txs = data.get("data", {}).get("data", [])
        except Exception as e:
            log.error(f"Failed to fetch Wallbit txs: {e}")
            return 0

        inserted_or_updated += await _upsert_wallbit_txs(session, conn, raw_txs)
        await session.commit()

    return inserted_or_updated


async def sync_all_wallbit_transactions(session: AsyncSession, connection_id: uuid.UUID) -> int:
    """Fetch ALL Wallbit transactions across all pages for a connection."""
    stmt = select(ProviderConnection).where(ProviderConnection.id == connection_id)
    result = await session.execute(stmt)
    conn = result.scalar_one_or_none()

    if not conn or conn.connection_type != "wallbit":
        return 0

    creds_json = decrypt(conn.credentials_encrypted).decode("utf-8")

    creds = json.loads(creds_json)
    api_key = creds.get("api_key")
    if not api_key:
        return 0

    settings = get_settings()
    url = settings.wallbit_base_url

    inserted_or_updated = 0
    current_page = 1
    total_pages = 1

    async with WallbitClient(api_key=api_key, base_url=url) as client:
        while current_page <= total_pages:
            try:
                data = await client._request("GET", f"/transactions?page={current_page}")
                page_data = data.get("data", {})
                raw_txs = page_data.get("data", [])

                # Update total pages if it's the first fetch
                if current_page == 1:
                    total_pages = page_data.get("pages", 1)

            except Exception as e:
                log.error(f"Failed to fetch Wallbit txs on page {current_page}: {e}")
                break

            if not raw_txs:
                break

            inserted_or_updated += await _upsert_wallbit_txs(session, conn, raw_txs)
            current_page += 1

        await session.commit()

    return inserted_or_updated


async def run_full_sync_pipeline(user_id: uuid.UUID) -> None:
    """Run full sync pipeline: Wallbit -> Classifier -> Context in a background task."""

    async with session_factory() as session:
        # 1. Sync Wallbit
        stmt = select(ProviderConnection).where(
            ProviderConnection.user_id == user_id, ProviderConnection.connection_type == "wallbit"
        )
        result = await session.execute(stmt)
        conns = result.scalars().all()

        for conn in conns:
            await sync_all_wallbit_transactions(session, conn.id)

    # 2. Run classifier on unclassified
    async with session_factory() as session:
        stmt = (
            select(CanonicalTransaction)
            .where(CanonicalTransaction.user_id == user_id)
            .where(~CanonicalTransaction.classifier.has_key("category"))
            .limit(100)  # batch of 100
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()

        if txs:
            payload = []
            for tx in txs:
                payload.append(
                    {
                        "uuid": str(tx.id),
                        "type": tx.type,
                        "direction": tx.direction,
                        "source_amount": float(tx.source_amount) if tx.source_amount else None,
                        "source_currency": tx.source_currency,
                        "dest_amount": float(tx.dest_amount) if tx.dest_amount else None,
                        "dest_unit": tx.dest_unit,
                        "merchant_hint": tx.merchant,
                        "description": tx.description,
                        "provider_payload": tx.raw_provider_payload,
                    }
                )

            # This could be batched, but we'll do 100 for MVP
            results = await classify_transactions(payload)

            tx_map = {str(tx.id): tx for tx in txs}

            for res in results:
                tx_id = res.get("uuid")
                if tx_id in tx_map:
                    tx = tx_map[tx_id]
                    tx.classifier = {
                        "category": res.get("category"),
                        "merchant": res.get("merchant"),
                        "recurrence_hint": res.get("recurrence_hint"),
                        "confidence": 0.95,
                    }

            # Mark profile dirty
            p_stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            p_res = await session.execute(p_stmt)
            profile = p_res.scalar_one_or_none()
            if profile:
                profile.is_dirty = True

            await session.commit()

    # 3. Recalculate context
    async with session_factory() as session:
        await recalculate_user_profile(session, user_id)
