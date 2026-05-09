import asyncio
from sqlalchemy import select
from app.persistence.session import get_session
from app.persistence.models.connections import ProviderConnection
from app.services.ingestion import sync_wallbit_transactions

async def main():
    async for session in get_session():
        stmt = select(ProviderConnection).where(ProviderConnection.connection_type == "wallbit")
        result = await session.execute(stmt)
        conns = result.scalars().all()
        
        for conn in conns:
            print(f"Syncing transactions for connection {conn.id}...")
            count = await sync_wallbit_transactions(session, conn.id)
            print(f"Synced {count} transactions.")

if __name__ == "__main__":
    asyncio.run(main())
