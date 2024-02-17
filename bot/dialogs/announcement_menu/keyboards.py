import operator

from aiogram_dialog.widgets.kbd import Group, Start, Select
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from bot.dialogs.main_menu import selected
from bot.dialogs.main_menu.states import UserAccount
from bot.utils.i18n_utils.i18n_format import I18NFormat


def select_announcement_type_kb(on_click):
    return Group(
        Select(
            Format("{item[1]}"),
            id="select_announcement_type",
            item_id_getter=operator.itemgetter(0),
            items='announcement_types_list',
            on_click=on_click
        ),
        width=1
    )