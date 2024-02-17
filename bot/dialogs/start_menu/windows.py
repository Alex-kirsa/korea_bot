from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Url, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.utils.i18n_utils.i18n_format import I18NFormat
from . import states, selected, getters, keyboards

FIRST_START_WINDOW = Window(
    I18NFormat('first_start_msg'),
    Url(Format('{channel_title}'), Format("{sub_channel_url}")),
    Button(I18NFormat('i_have_sub'), id='i_have_sub', on_click=selected.continue_to_menu),
    state=states.FirstStartWindow.sub_on_channel,
    getter=getters.get_sub_channel_url,
)