from aiogram import Bot

from bot.db import Repo
from bot.db.requests import user_requests
from bot.utils.logging import logging


async def send_admins(bot: Bot, repo: Repo, message: str):
    admins = await repo.user_repo.get_admins()
    for admin in admins:
        try:
            await bot.send_message(admin.user_id, message)
        except Exception as e:
            logging.exception(e)
            continue
