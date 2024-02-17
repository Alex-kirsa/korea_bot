from aiogram import Bot
from arq import cron
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from bot.services.scheduler.func import send_schedule_message
from configreader import config, RedisConfig
from bot.db.base import metadata


async def startup(ctx):
    engine = create_async_engine(
        str(config.postgredsn), future=True, echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    # Creating DB connections pool
    db_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    ctx["db_factory"] = db_factory
    ctx['bot'] = Bot(token=config.bot_token, parse_mode='HTML')


async def shutdown(ctx):
    # bot: Bot = ctx['bot']
    # await bot.session.close()
    pass


class WorkerSettings:
    redis_settings = RedisConfig.pool_settings
    on_startup = startup
    on_shutdown = shutdown
    functions = [send_schedule_message,]
    cron_jobs = [
        cron('bot.services.scheduler.func.send_schedule_message', minute={0, 15, 30, 45}, max_tries=3, run_at_startup=True)
    ]
