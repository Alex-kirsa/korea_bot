from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.dialogs.announcement_menu.states import AnnouncementPost, CreateAd, CreatePost
from bot.dialogs.main_menu import states
from bot.utils.constants import PostTypesEnum, PostStatus


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
    if item_id == 'announcement':
        scheduled_posts = await repo.post_repo.get_scheduled_post_created_last_24_hours(call.from_user.id,
                                                                                        announcement_type=[
                                                                                            PostTypesEnum.ANNOUNCEMENT_VEHICLE,
                                                                                            PostTypesEnum.ANNOUNCEMENT_VACANCY,
                                                                                            PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE,
                                                                                                ])
        if len(scheduled_posts) >= 3:
            await call.answer(i18n.get('you_can_create_only_3_announcement_per_day'), show_alert=True)
            return
    elif item_id == 'post':
        scheduled_posts = await repo.post_repo.get_scheduled_post_created_last_24_hours(call.from_user.id,
                                                                                        announcement_type=[PostTypesEnum.POST])
        if len(scheduled_posts) >= 3:
            await call.answer(i18n.get('you_can_create_only_3_posts_per_day'), show_alert=True)
            return
    await manager.start(states_mapping[item_id])


async def on_select_post_request(call: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    manager.dialog_data.update(schedule_post_id=int(item_id))
    await manager.switch_to(states.UserPostRequests.show_post_details)


async def on_send_once_more(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    schedule_post_id = manager.dialog_data.get('schedule_post_id')
    schedule_post_model = await repo.post_repo.get_schedule_post(schedule_post_id)
    if schedule_post_model.announcement_type == PostTypesEnum.AD:
        user_model = await repo.user_repo.get_user(schedule_post_model.user_id)
        ad_price = await repo.bot_settings_repo.get_bot_setting('ad_price')
        if user_model.balance < int(ad_price.value):
            await call.answer(i18n.get('not_enough_balance'), show_alert=True)
            return
        await repo.user_repo.minus_user_balance(schedule_post_model.user_id, int(ad_price.value))
    await repo.post_repo.update_schedule_post_status(schedule_post_id, PostStatus.WAIT_ACCEPT)
    await call.answer(i18n.get('your_ask_request_accept'), show_alert=True)
    await manager.switch_to(states.UserPostRequests.show_post_details)


async def on_show_post(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    schedule_post_id = manager.dialog_data.get('schedule_post_id')
    schedule_post_model = await repo.post_repo.get_schedule_post(schedule_post_id)
    await manager.start(states.ShowPost.show_post_text, data={'post_text': schedule_post_model.text_for_publish})


async def on_edit_post(call: CallbackQuery, widget: Button, manager: DialogManager):
    await manager.start(states.UpdatePostText.enter_text, data=manager.dialog_data)


async def on_enter_new_post_text(message: Message, widget: ManagedTextInput, manager: DialogManager, message_text):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    schedule_post_mdoel = await repo.post_repo.get_schedule_post(manager.start_data.get('schedule_post_id'))
    raw_post_id = schedule_post_mdoel.post_id
    raw_post_model_mapping = {
        PostTypesEnum.AD: await repo.post_repo.get_ad_post(raw_post_id),
        PostTypesEnum.POST: await repo.post_repo.get_post(raw_post_id),
    }
    update_raw_post_mapping = {
        PostTypesEnum.AD: await repo.post_repo.update_ad_text(raw_post_id, message.html_text),
        PostTypesEnum.POST: await repo.post_repo.update_post_text(raw_post_id, message.html_text)
    }
    raw_post_model = raw_post_model_mapping[schedule_post_mdoel.announcement_type]
    updated_post = update_raw_post_mapping[schedule_post_mdoel.announcement_type]
    await repo.post_repo.update_schedule_post_text(schedule_post_mdoel.id, message.html_text)
    await repo.post_repo.update_schedule_post_status(schedule_post_mdoel.id, PostStatus.WAIT_ACCEPT)
    await message.answer(i18n.get('post_text_was_succssesfully_changed'))
    await manager.done()


