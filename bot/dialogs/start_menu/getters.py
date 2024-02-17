from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.utils.admins import send_admins


async def get_sub_channel_url(dialog_manager: DialogManager, i18n: I18nContext, repo: Repo, bot: Bot, **middleware_data):
    sub_channel_url = await repo.bot_settings_repo.get_bot_setting('sub_channel_url')
    sub_channel_id = await repo.bot_settings_repo.get_bot_setting('sub_channel_id')
    # try:
    channel_info = await bot.get_chat(int(sub_channel_id.value))
    # except Exception as e:
    #     await bot.send_message(dialog_manager.event.from_user.id, "Бот временно недоступен, попробуйте позже")
    #     await send_admins(bot, repo, "Ошибка получения информации о канале. \n\n"
    #                                  "<i>Скорее всего бот был удален из канала или наблюдаются проблемы с серверами телеграма</i>")
    #     return dict()
    return {
        'sub_channel_url': sub_channel_url.value,
        'channel_title': channel_info.title
    }
