import datetime

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.models import *


class PurchaseRequestsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_purchase(self, user_id: int, sender_name: str, amount: int, datetime_purchase: datetime.datetime) -> int:
        stmt = TopUpOperations(user_id=user_id, sender_name=sender_name, amount=amount, date=datetime_purchase)
        self.session.add(stmt)
        await self.session.commit()

    async def change_purchase_status(self, purchase_id: int, status: PurchaseStatus):
        query = update(TopUpOperations).where(TopUpOperations.id == purchase_id).values(status=status)
        await self.session.execute(query)
        await self.session.commit()

    async def get_purchase(self, purchase_id: int):
        query = select(TopUpOperations).where(TopUpOperations.id == purchase_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all_purchases(self):
        query = select(TopUpOperations)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_purchases_with_status(self, status: PurchaseStatus):
        query = select(TopUpOperations).where(TopUpOperations.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()
