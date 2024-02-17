from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel

from bot.utils.i18n_utils.i18n_format import I18NFormat
from . import states, getters, keyboards, selected


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