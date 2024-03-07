# -*- coding: utf-8 -*-
import asyncio
import logging
import os

import aiohttp_cors
from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisEventIsolation, RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiohttp import web
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from bot.db.base import metadata
from bot.db.requests.bot_settings import add_default_bot_settings
from bot.dialogs import dialogs_includer
from bot.handlers import include_handlers
from bot.handlers.user_handlers import handle_create_vacancy_post, handle_create_real_estate_post, handle_create_vehicle_post, handle_purchase
# from bot.db.requests import channel_requests
from bot.middlewares.i18n_dialog import RedisI18nMiddleware
from bot.utils.set_bot_commands import set_default_commands
from configreader import config
# from .dialogs import include_dialogs
# from .handlers import include_handlers_routers
from .middlewares.db import DbSessionMiddleware
from .utils.i18n_utils.i18n_format import make_i18n_middleware
from .utils.redis.redis import redis


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(
        f"{config.webhook_base_url}{config.webhook_path}",
        secret_token=config.webhook_secret,
    )


@logger.catch
async def main():
    engine = create_async_engine(str(config.postgredsn), future=True, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    # Creating DB connections pool
    db_pool = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, autoflush=False)
    async with db_pool() as session:
        await add_default_bot_settings(session)
    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    # Choosing FSM storage
    key_builder = DefaultKeyBuilder(with_destiny=True, with_bot_id=True)
    storage = RedisStorage(redis=redis, key_builder=key_builder)
    event_isolation = RedisEventIsolation(redis, key_builder=key_builder)
    dp = Dispatcher(storage=storage, events_isolation=event_isolation)
    dp.startup.register(on_startup)
    dp["dp"] = dp

    path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
    core = FluentRuntimeCore(path=path_to_locales, default_locale='uk')
    i18n_middleware = RedisI18nMiddleware(
        core=core,
        default_locale="uk",
        redis=redis,
    )
    i18n_dialog_middleware = make_i18n_middleware(path_to_locales)
    router = Router(name=__name__)
    # Allow interaction in private chats (not groups or channels) only
    dp.message.filter(F.chat.type == "private")

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))
    dp.update.middleware(DbSessionMiddleware(db_pool))
    dp.message.middleware(i18n_dialog_middleware)
    dp.callback_query.middleware(i18n_dialog_middleware)
    dp.update.middleware(i18n_dialog_middleware)
    # Router including
    include_handlers(router)
    dialogs_includer(router)
    dialogs_factory = setup_dialogs(router)
    dp.include_router(router)
    i18n_middleware.setup(dispatcher=dp)

    # await bot.delete_webhook(drop_pending_updates=True)
    await set_default_commands(bot)

    # Имплементируем планировщик задач
    # redis_pool = await create_pool(RedisConfig.pool_settings)
    # dp["arqredis"] = redis_pool
    dp["session_pool"] = db_pool

    app = web.Application(logger=logger)
    app['bot'] = bot
    app['db_factory'] = db_pool
    app['dp'] = dp
    app['dialogs_factory'] = dialogs_factory
    app['core'] = core
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook_secret,
    ).register(app, path=config.webhook_path)
    app.router.add_post(config.add_post_vacancy_webhook, handle_create_vacancy_post)
    app.router.add_post(config.add_post_purchase_webhook, handle_purchase)
    app.router.add_post(config.add_post_vehicle_webhook, handle_create_vehicle_post)
    app.router.add_post(config.add_post_real_estate_webhook, handle_create_real_estate_post)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*"
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)
    setup_application(app, dp, bot=bot)
    # Start bot
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner, host=config.webhook_host, port=config.webhook_port
    )

    await site.start()
    logger.info("Bot started!")
    # await dp.start_polling(bot)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
