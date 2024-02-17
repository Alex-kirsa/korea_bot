from aiogram_dialog import Dialog
from . import windows


def main_menu_dialogs():
    return [
        Dialog(
            windows.main_menu
        ),
        Dialog(
            windows.user_account
        ),
        Dialog(
            windows.user_post_requests
        )

    ]
