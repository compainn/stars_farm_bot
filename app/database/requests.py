from app.database.models import async_session, User
from sqlalchemy import select
from config import INVITE_PRIZE


async def set_user(tg_id: int, username: str, inviter_id: int = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(
                tg_id=tg_id,
                username=username
            )
            session.add(user)
            await session.flush()

            if inviter_id:
                inviter = await session.scalar(select(User).where(User.tg_id == inviter_id))
                if inviter:
                    user.invited_by = inviter_id
                    inviter.balance += INVITE_PRIZE
                    inviter.referrals_count += 1

            await session.commit()

        return user





async def get_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def add_stars(tg_id: int, amount: float):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.balance += amount
            await session.commit()



async def increment_active_requests(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.active_requests += 1
            await session.commit()

async def decrement_active_requests(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user and user.active_requests > 0:
            user.active_requests -= 1
            await session.commit()
