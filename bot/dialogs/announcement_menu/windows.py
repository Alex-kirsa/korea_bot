from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, WebApp, Back
from aiogram_dialog.widgets.text import Format

from bot.utils.i18n_utils.i18n_format import I18NFormat
from . import states, getters, keyboards, selected


def select_announcement_type_window():
    return Window(
        I18NFormat("you_are_in_announcement_posting_menu"),
        keyboards.select_announcement_type_kb(selected.on_select_announcement_type),
        Cancel(I18NFormat('back')),
        state=states.AnnouncementPost.select_announcement_type,
        getter=getters.get_announcement_type,
    )


def show_webapp_window():
    return Window(
        I18NFormat("fill_the_form"),
        WebApp(
            I18NFormat('fill_the_form_btn'),
            Format('{form_url}')
        ),
        Back(I18NFormat('back')),
        state=states.AnnouncementPost.show_announcement_webapp,
        getter=getters.get_form_data,
    )


def enter_ask_window():
    return Window(
        I18NFormat("enter_ask_for_publish"),
        TextInput(id='enter_ask', on_success=selected.on_enter_ask_for_publish),
        Cancel(I18NFormat('back')),
        state=states.CreatePost.enter_ask_for_publish,

    )


def enter_ad_window():
    return Window(
        I18NFormat("enter_ad_text"),
        TextInput(id='enter_ad_text', on_success=selected.on_enter_ad_message),
        Cancel(I18NFormat('back')),
        state=states.CreateAd.enter_ad_message,
    )

