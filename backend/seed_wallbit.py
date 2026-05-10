import asyncio
import json
import os

from dotenv import load_dotenv

from app.persistence.crypto import encrypt
from app.persistence.models.connections import ProviderConnection
from app.persistence.models.users import User, UserProfile
from app.persistence.session import get_session

load_dotenv()


async def main():
    api_key = os.getenv("WALLBIT_API_KEY")
    if not api_key:
        print("Missing WALLBIT_API_KEY")
        return

    creds = {"api_key": api_key}
    creds_encrypted = encrypt(json.dumps(creds).encode("utf-8"))

    async for session in get_session():
        # Create user
        user = User(display_name="Demo User")
        session.add(user)
        await session.flush()

        # Create profile
        profile = UserProfile(user_id=user.id)
        session.add(profile)

        # Create connection
        conn = ProviderConnection(
            user_id=user.id,
            connection_type="wallbit",
            label="Mi Wallbit",
            auth_kind="api_key",
            credentials_encrypted=creds_encrypted,
            credentials_kid="v1",
            status="healthy",
        )
        session.add(conn)
        await session.commit()
        print(f"Seeded User {user.id} and Connection {conn.id}")


if __name__ == "__main__":
    asyncio.run(main())
