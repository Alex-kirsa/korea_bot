import datetime
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramServerError, TelegramEntityTooLarge
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_i18n.cores import FluentRuntimeCore, BaseCore




async def check_enough_rights(bot_rights):
    can_post_message = bot_rights.can_post_messages
    can_delete_messages = bot_rights.can_delete_messages
    can_edit_message = bot_rights.can_edit_messages
    can_invite_users = bot_rights.can_invite_users
    if (
            can_post_message in (True, None)
            and can_delete_messages in (True, None)
            and can_edit_message in (True, None)
            and can_invite_users in (True, None)
    ):
        return True
    else:
        return False


def convert_str_date_in_datetime(datetime_str: str, hour: int | str = None, minute: int | str = None):
    datetime_format = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
    if hour:
        datetime_format = datetime_format.replace(hour=int(hour))
    if minute:
        datetime_format = datetime_format.replace(minute=int(minute))
    return datetime_format


