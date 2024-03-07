import operator

from aiogram_dialog.widgets.kbd import Group, Start, Select, ScrollingGroup, Button, WebApp
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from bot.dialogs.main_menu import selected
from bot.dialogs.main_menu.states import UserAccount, TopUpBalance, UserPostRequests
from bot.utils.constants import PostTypesEnum, PostStatus
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
        width=1,
        hide_on_single_page=True

    )


def actions_with_post_kb():
    return Group(
        Button(I18NFormat('show_post'), id='show_post', on_click=selected.on_show_post),
        # Group(
            # WebApp(I18NFormat('edit_post'), id='edit_post', url=Format('{edit_post_url}'),
            #        when=F['post_type_enum'].in_([PostTypesEnum.ANNOUNCEMENT_VACANCY,
            #                                      PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE,
            #                                      PostTypesEnum.ANNOUNCEMENT_VEHICLE])),
        #     Button(I18NFormat('edit_post'), id='edit_simple_post', on_click=selected.on_edit_post,
        #            when=F['post_type_enum'].in_([PostTypesEnum.POST, PostTypesEnum.AD])),
        #     when='can_edit'
        # ),
        Button(I18NFormat('send_once_more'), id='send_once_more', on_click=selected.on_send_once_more,
               when=F['post_status_enum'].in_([PostStatus.PUBLISHED, PostStatus.REJECTED])),

    )
