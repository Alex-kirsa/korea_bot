from aiogram.types import User
from aiogram_dialog import DialogManager

from bot.db import Repo
from bot.utils.constants import ADS


async def get_announcement_type(dialog_manager: DialogManager, **middleware_data):
    return {
        'announcement_types_list': [
            (key, value) for key, value in ADS.items()
        ]
    }


async def get_form_data(dialog_manager: DialogManager, repo: Repo, **middleware_data):
    form_url = await repo.bot_settings_repo.get_bot_setting(f'webapp_url_{dialog_manager.dialog_data["announcement_type"]}')
    announcement_type_mapping = {
        'vacancy': 'вакансию',
        'real_estate': 'недвижимость',
        'vehicle': 'транспорт',
    }
    return {
        'form_url': form_url.value,
        "announcement_type": announcement_type_mapping[dialog_manager.dialog_data["announcement_type"]]
    }
