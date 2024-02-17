from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_i18n import I18nContext

from bot.db import Repo
from bot.dialogs.main_menu.states import MainMenu
from bot.dialogs.start_menu.states import FirstStartWindow
from bot.middlewares.throttling import ThrottlingMiddleware

router = Router()
router.message.middleware(ThrottlingMiddleware())


@router.message(CommandStart())
async def start(message: Message, i18n: I18nContext, dialog_manager: DialogManager, repo: Repo, bot: Bot):
    user_model = await repo.user_repo.get_user(message.from_user.id)
    if not user_model:
        return await dialog_manager.start(FirstStartWindow.sub_on_channel, mode=StartMode.RESET_STACK)
    channel_id_for_sub = await repo.bot_settings_repo.get_bot_setting('sub_channel_id')
    user_sub_status = await bot.get_chat_member(int(channel_id_for_sub.value), message.from_user.id)
    if user_sub_status.status in ['member', 'administrator', 'creator']:
        await dialog_manager.start(MainMenu.select_action, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(FirstStartWindow.sub_on_channel, mode=StartMode.RESET_STACK)
