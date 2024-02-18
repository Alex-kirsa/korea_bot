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
            windows.user_post_requests,
            windows.post_request_data
        ),
        Dialog(
          windows.show_post_text
        ),
        Dialog(windows.send_money_for_topup),
        Dialog(windows.update_post),


    ]
