from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.dialogs.announcement_menu.states import AnnouncementPost
from bot.utils.admins import send_admins
from bot.utils.constants import PostTypesEnum


async def on_select_announcement_type(call: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    manager.dialog_data.update(announcement_type=item_id)
    await manager.switch_to(AnnouncementPost.show_announcement_webapp)


async def on_enter_ask_for_publish(message: Message, widget: ManagedTextInput, manager: DialogManager, message_text: str):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    bot: Bot = manager.middleware_data['bot']
    post_id = await repo.post_repo.add_post(message.chat.id, message_text)
    await repo.post_repo.add_scheduled_post(message.chat.id, post_id, PostTypesEnum.POST)
    await send_admins(bot, repo, i18n.get('new_post_request'))
    await message.answer(i18n.get('your_ask_request_accept'))
    await manager.done()


async def on_enter_ad_message(message: Message, widget: ManagedTextInput, manager: DialogManager, message_text: str):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    bot: Bot = manager.middleware_data['bot']
    manager.dialog_data.update(post_text=message_text)
    post_id = await repo.post_repo.add_post(message.chat.id, message_text)
    await repo.post_repo.add_scheduled_post(message.chat.id, post_id, PostTypesEnum.AD)
    ad_price = await repo.bot_settings_repo.get_bot_setting('ad_price')
    await repo.user_repo.minus_user_balance(message.chat.id, float(ad_price.value))
    await send_admins(bot, repo, i18n.get('new_ad_request'))
    await message.answer(i18n.get('your_ad_request_accept', price=ad_price.value))
    await manager.done()
