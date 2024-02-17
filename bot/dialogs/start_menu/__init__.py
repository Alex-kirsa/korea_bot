from aiogram_dialog import Dialog
from . import windows


def start_dialogs():
    return [
        Dialog(
            windows.FIRST_START_WINDOW
        )
    ]
