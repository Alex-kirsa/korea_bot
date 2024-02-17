from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.dialogs.main_menu import states


async def continue_to_menu(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    bot: Bot = manager.middleware_data['bot']
    _: I18nContext = manager.middleware_data['i18n']
    channel_id_for_sub = await repo.bot_settings_repo.get_bot_setting('sub_channel_id')
    user_sub_status = await bot.get_chat_member(int(channel_id_for_sub.value), call.from_user.id)
    user_exist = await repo.user_repo.get_user(call.from_user.id)
    if user_sub_status.status in ['member', 'administrator', 'creator']:
        if not user_exist:
            await repo.user_repo.add_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
        return await manager.start(states.MainMenu.select_action)
    await call.answer(_.get("you_doesnt_sub"), show_alert=True)
