from aiogram import Router
from . import start_menu, main_menu, announcement_menu


def dialogs_includer(router: Router):
    router.include_routers(*start_menu.start_dialogs(), *main_menu.main_menu_dialogs(), *announcement_menu.announcement_menu_dialogs())
