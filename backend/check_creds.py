import asyncio

from sqlalchemy import select

from app.persistence.crypto import decrypt
from app.persistence.models.connections import ProviderConnection
from app.persistence.session import get_session


async def main():
    async for session in get_session():
        stmt = select(ProviderConnection)
        result = await session.execute(stmt)
        conn = result.scalar_one_or_none()
        if conn:
            print("Encrypted:", conn.credentials_encrypted)
            try:
                dec = decrypt(conn.credentials_encrypted)
                print("Decrypted:", dec)
            except Exception as e:
                print("Decrypt error:", e)


if __name__ == "__main__":
    asyncio.run(main())
