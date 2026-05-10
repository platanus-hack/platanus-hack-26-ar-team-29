import asyncio

from sqlalchemy import select

from app.agents.classifier_agent import classify_transactions
from app.persistence.models.ledger import CanonicalTransaction
from app.persistence.models.users import UserProfile
from app.persistence.session import get_session


async def process_unclassified():
    async for session in get_session():
        # 1. Fetch unclassified (where classifier = '{}')
        # JSONB empty dict comparison is best done with path extracting or literal casting,
        # but since we initialized with '{}'::jsonb we can just check length or specific key.
        stmt = (
            select(CanonicalTransaction)
            .where(~CanonicalTransaction.classifier.has_key("category"))
            .limit(50)
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()

        if not txs:
            print("No unclassified transactions found.")
            return

        print(f"Found {len(txs)} unclassified transactions. Running classifier agent...")

        # Prepare payload
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

        # Classify
        results = await classify_transactions(payload)

        print(f"Classifier agent returned {len(results)} results.")

        # 2. Update DB
        tx_map = {str(tx.id): tx for tx in txs}
        users_to_mark_dirty = set()

        for res in results:
            tx_id = res.get("uuid")
            if tx_id in tx_map:
                tx = tx_map[tx_id]
                tx.classifier = {
                    "category": res.get("category"),
                    "merchant": res.get("merchant"),
                    "recurrence_hint": res.get("recurrence_hint"),
                    "confidence": 0.95,  # hardcoded for LLM
                }
                users_to_mark_dirty.add(tx.user_id)

        # 3. Mark user profiles as dirty so the context recalculator picks them up
        for uid in users_to_mark_dirty:
            p_stmt = select(UserProfile).where(UserProfile.user_id == uid)
            p_res = await session.execute(p_stmt)
            profile = p_res.scalar_one_or_none()
            if profile:
                profile.is_dirty = True

        await session.commit()
        print("Classification saved to database.")


if __name__ == "__main__":
    asyncio.run(process_unclassified())
