import asyncio

from sqlalchemy import select

from app.persistence.models.users import UserProfile
from app.persistence.session import get_session
from app.services.context import recalculate_user_profile


async def main():
    async for session in get_session():
        stmt = select(UserProfile).where(UserProfile.is_dirty)
        result = await session.execute(stmt)
        profiles = result.scalars().all()

        for profile in profiles:
            await recalculate_user_profile(session, profile.user_id)


if __name__ == "__main__":
    asyncio.run(main())
