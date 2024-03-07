import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.models import *


class BotSettingsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_bot_setting(self, key: str):
        query = select(BotSettings).where(
            BotSettings.key == key
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def add_setting(self, key: str, value: str):
        query = insert(BotSettings).values(
            key=key,
            value=value
        ).on_conflict_do_nothing()
        await self.session.execute(query)
        await self.session.commit()

    async def update_setting(self, key: str, value: str):
        query = update(BotSettings).where(
            BotSettings.key == key
        ).values(
            value=value
        )
        await self.session.execute(query)
        await self.session.commit()


async def add_default_bot_settings(session: AsyncSession):
    default_settings = {
        'ad_price': '100',
        'sub_channel_url': 'https://t.me/test1231324124',
        'sub_channel_id': str(-1001960731769),
        'webapp_url_vacancy': "https://webapp-forms.netlify.app/job-posting-form",
        'webapp_url_real_estate': 'https://webapp-forms.netlify.app/real-estate-submission-form',
        'webapp_url_vehicle': 'https://webapp-forms.netlify.app/vehicle-submission-form',
        "webapp_url_purchase": "https://webapp-forms.netlify.app/payment-confirmation-form",
        "card_number": "1234 5678 1234 5678"


    }
    for key, value in default_settings.items():
        query = insert(BotSettings).values(
            key=key,
            value=value
        ).on_conflict_do_nothing()
        await session.execute(query)
    await session.commit()
    return
