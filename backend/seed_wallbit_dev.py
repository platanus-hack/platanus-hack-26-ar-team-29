import asyncio
import os
import json
import uuid
from dotenv import load_dotenv

from app.persistence.session import get_session
from app.persistence.models.users import User, UserProfile
from app.persistence.models.connections import ProviderConnection
from app.persistence.crypto import encrypt

load_dotenv()

from sqlalchemy import select


async def main():
    api_key = os.getenv("WALLBIT_API_KEY")
    if not api_key:
        print("Missing WALLBIT_API_KEY")
        return

    creds = {"api_key": api_key}
    creds_encrypted = encrypt(json.dumps(creds).encode("utf-8"))

    dev_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    async for session in get_session():
        stmt = select(User).where(User.id == dev_user_id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(id=dev_user_id, display_name="Dev User")
            session.add(user)
            await session.flush()

        stmt = select(UserProfile).where(UserProfile.user_id == dev_user_id)
        profile = (await session.execute(stmt)).scalar_one_or_none()
        if not profile:
            profile = UserProfile(user_id=dev_user_id)
            session.add(profile)

        stmt = select(ProviderConnection).where(ProviderConnection.user_id == dev_user_id)
        conn = (await session.execute(stmt)).scalar_one_or_none()
        if not conn:
            conn = ProviderConnection(
                user_id=dev_user_id,
                connection_type="wallbit",
                label="Mi Wallbit",
                auth_kind="api_key",
                credentials_encrypted=creds_encrypted,
                credentials_kid="v1",
                status="healthy",
            )
            session.add(conn)
        else:
            conn.credentials_encrypted = creds_encrypted

        await session.commit()
        print(f"Seeded User {dev_user_id} and Connection {conn.id}")


if __name__ == "__main__":
    asyncio.run(main())
