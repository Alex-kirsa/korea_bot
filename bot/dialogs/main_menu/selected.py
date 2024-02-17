from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.dialogs.announcement_menu.states import AnnouncementPost, CreateAd, CreatePost
from bot.utils.constants import PostTypesEnum


async def on_select_post_type(call: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    states_mapping = {
        'announcement': AnnouncementPost.select_announcement_type,
        'ad': CreateAd.enter_ad_message,
        'post': CreatePost.enter_ask_for_publish
    }
    if item_id == PostTypesEnum.AD:
        user_model = await repo.user_repo.get_user(call.from_user.id)
        ad_price = await repo.bot_settings_repo.get_bot_setting('ad_price')
        if user_model.balance < int(ad_price.value):
            await call.answer(i18n.get('not_enough_balance'), show_alert=True)
            return
    await manager.start(states_mapping[item_id])


async def on_select_post_request(call: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    schedule_post_model = await repo.post_repo.get_schedule_post(int(item_id))

