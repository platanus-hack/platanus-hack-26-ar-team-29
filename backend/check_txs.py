import asyncio

from sqlalchemy import select

from app.persistence.models.ledger import CanonicalTransaction
from app.persistence.session import get_session


async def main():
    async for session in get_session():
        stmt = select(CanonicalTransaction)
        result = await session.execute(stmt)
        txs = result.scalars().all()
        for tx in txs:
            print(
                f"Tx {tx.external_id} | {tx.type} | {tx.classifier.get('category')} | {tx.classifier.get('merchant')}"
            )


if __name__ == "__main__":
    asyncio.run(main())
