from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.utils.constants import POST_TYPES, PostTypesEnum


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
        user_posts_list.append((post.id, f"#{post.id}-{i18n.get(post.status)}"))
    return {
        'post_requests_list': user_posts_list
    }


