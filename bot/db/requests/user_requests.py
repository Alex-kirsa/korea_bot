import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.models import *


class UserRequestsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user_id: int, full_name: str, username: str | None):
        query = insert(Users).values(
            user_id=user_id,
            fullname=full_name,
            username=username,
            sub_status_on_channel=True
        ).on_conflict_do_nothing()
        await self.session.execute(query)
        await self.session.commit()

    async def get_user(self, user_id: int):
        query = select(Users).where(
            Users.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_users(self):
        query = select(Users)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_admins(self):
        query = select(Admins)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def minus_user_balance(self, user_id: int, amount: float):
        query = update(Users).where(
            Users.user_id == user_id
        ).values(
            balance=Users.balance - amount
        )
        await self.session.execute(query)
        await self.session.commit()

    async def plus_user_balance(self, user_id: int, amount: float):
        query = update(Users).where(
            Users.user_id == user_id
        ).values(
            balance=Users.balance + amount
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_admin_with_login_and_password(self, login: str, password: str):
        query = select(Admins).where(
            Admins.login == login,
            Admins.password == password
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_admin_by_login(self, login: str):
        query = select(Admins).where(
            Admins.login == login
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_last_10_users_desc(self):
        query = select(Users).order_by(Users.user_id.desc()).limit(10)
        result = await self.session.execute(query)
        return result.scalars().all()
