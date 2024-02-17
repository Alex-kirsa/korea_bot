from aiogram_dialog import Dialog

from bot.dialogs.announcement_menu import windows


def announcement_menu_dialogs():
    return [
        Dialog(
            windows.select_announcement_type_window(),
            windows.show_webapp_window(),
        ),
        Dialog(
            windows.enter_ask_window(),
        ),
        Dialog(
            windows.enter_ad_window()
        )

    ]
