from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Back, StubScroll, Group, NumberedPager, WebApp
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Multi
from magic_filter import F

from bot.utils.i18n_utils.i18n_format import I18NFormat
from . import states, getters, keyboards, selected
from ...utils.constants import PostTypesEnum

main_menu = Window(
    I18NFormat("start_msg"),
    keyboards.main_menu_kb(),
    state=states.MainMenu.select_action,
    getter=getters.get_main_menu,
)

user_account = Window(
    I18NFormat("user_account_info"),
    keyboards.user_account_kb(),
    Cancel(I18NFormat('back')),
    state=states.UserAccount.show_account_info,
    getter=getters.get_user_account_info,
)

user_post_requests = Window(
    I18NFormat("all_user_post_requests"),
    keyboards.user_post_requests_kb(selected.on_select_post_request),
    Cancel(I18NFormat('back')),
    state=states.UserPostRequests.show_user_requests,
    getter=getters.get_user_post_requests,
)

post_request_data = Window(
    I18NFormat("post_request_info"),
    keyboards.actions_with_post_kb(),
    Back(I18NFormat('back')),
    state=states.UserPostRequests.show_post_details,
    getter=getters.get_post_request_data,
)

show_post_text = Window(
    Format("{post_text}"),
    DynamicMedia(selector="media"),
    StubScroll(id="pages", pages="media_count"),
    Group(NumberedPager(scroll="pages", when=F["pages"] > 1), width=8),
    Cancel(I18NFormat('back')),
    state=states.ShowPost.show_post_text,
    getter=getters.get_post_text,
)

send_money_for_topup = Window(
    I18NFormat('send_money_for_topup'),
    WebApp(I18NFormat('i_have_paid'), url=Format('{purchase_pruf_url}')),
    Cancel(I18NFormat('back')),
    state=states.TopUpBalance.enter_amount,
    getter=getters.get_topup_amount,
)

update_post = Window(
    Multi(
        I18NFormat('enter_new_post_text', when=F['post_type'].in_([PostTypesEnum.POST])),
        I18NFormat('enter_new_ad_text', when=F['post_type'].in_([PostTypesEnum.AD])),
    ),
    TextInput(id="enter_new_post_text", on_success=selected.on_enter_new_post_text),
    Cancel(I18NFormat('back')),
    state=states.UpdatePostText.enter_text,
    getter=getters.get_post_type,
)
