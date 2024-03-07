from aiogram.enums import ContentType
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.utils.constants import POST_TYPES, PostTypesEnum, post_types_mapping, ad_post_status_mapping, webapp_urls_mapping, BotSettingsEnum


async def get_main_menu(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    return {
        'post_types_list': [
            (key, value) for key, value in POST_TYPES.items()
        ]
    }


async def get_user_account_info(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    user = await repo.user_repo.get_user(event_from_user.id)
    user_post = await repo.post_repo.get_all_user_post(event_from_user.id)
    return {
        'balance': user.balance,
        'rating': user.rating,
        'posts': len(user_post) if user_post else 0
    }


async def get_user_post_requests(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    user_posts = await repo.post_repo.get_all_user_post(event_from_user.id)
    i18n: I18nContext = middleware_data['i18n']
    user_posts_list = []

    for post in user_posts:
        user_posts_list.append((post.id, f"#{post.id}-{post.text_for_publish[:20]}"))
    return {
        'post_requests_list': user_posts_list
    }


async def get_post_request_data(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    schedule_post_id = dialog_manager.dialog_data.get('schedule_post_id')
    schedule_post_model = await repo.post_repo.get_schedule_post(schedule_post_id)
    web_app_url = await repo.bot_settings_repo.get_bot_setting(webapp_urls_mapping.get(schedule_post_model.announcement_type))
    dialog_manager.dialog_data.update(post_type=schedule_post_model.announcement_type)
    return {
        'schedule_post_id': schedule_post_id,
        'post_type': post_types_mapping[schedule_post_model.announcement_type],
        'post_type_enum': schedule_post_model.announcement_type,
        'post_status': ad_post_status_mapping[schedule_post_model.status],
        'post_status_enum': schedule_post_model.status,
        'published_datetime': schedule_post_model.published_datetime.strftime("%d.%m.%Y %H:%M") if schedule_post_model.published_datetime else 'Не опубликован',
        'edit_post_url': web_app_url.value if web_app_url else None
    }


async def get_post_text(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    start_data = dialog_manager.start_data
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    medias_list = start_data.get('medias_list', [])
    media_object = None
    if medias_list:
        media_object = MediaAttachment(
            url=medias_list[media_number],
            type=ContentType.PHOTO,
        )
    return {
        'post_text': start_data.get('post_text'),
        'media': media_object,
        "media_number": media_number + 1,
        'media_count': len(medias_list)
    }


async def get_topup_amount(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    one_ad_price = await repo.bot_settings_repo.get_bot_setting(BotSettingsEnum.AD_PRICE)
    purhcace_webapp_url = await repo.bot_settings_repo.get_bot_setting(BotSettingsEnum.WEBAPP_URL_PURCHASE)
    card_number = await repo.bot_settings_repo.get_bot_setting(BotSettingsEnum.CARD_NUMBER)
    return {
        'one_ad_price': float(one_ad_price.value),
        'purchase_pruf_url': purhcace_webapp_url.value,
        "card_number": card_number.value
    }


async def get_post_type(dialog_manager: DialogManager, repo: Repo, event_from_user: User, **middleware_data):
    return {
        'post_type': dialog_manager.start_data.get('post_type')
    }
