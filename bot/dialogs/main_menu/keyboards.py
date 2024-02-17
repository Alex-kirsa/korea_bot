import operator

from aiogram_dialog.widgets.kbd import Group, Start, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from bot.dialogs.main_menu import selected
from bot.dialogs.main_menu.states import UserAccount, TopUpBalance, UserPostRequests
from bot.utils.i18n_utils.i18n_format import I18NFormat


def main_menu_kb():
    return Group(
        Select(
            Format("{item[1]}"),
            id="select_action",
            item_id_getter=operator.itemgetter(0),
            items='post_types_list',
            on_click=selected.on_select_post_type
        ),
        Start(
            I18NFormat('user_account'),
            id="user_account",
            state=UserAccount.show_account_info
        ),
        width=1
    )


def user_account_kb():
    return Group(
        Start(
            I18NFormat('top_up_balance'),
            id="top_up_balance",
            state=TopUpBalance.enter_amount
        ),
        Start(
            I18NFormat('my_requests_for_post'),
            id="my_requests_for_post",
            state=UserPostRequests.show_user_requests,
            when='posts'
        )
    )


def user_post_requests_kb(on_click):
    return ScrollingGroup(
        Select(
            Format("{item[1]}"),
            id="show_post_details",
            item_id_getter=operator.itemgetter(0),
            items='post_requests_list',
            on_click=on_click
        ),
        id='user_posts_s_g',
        height=6,
        width=1

    )