from aiogram.fsm.state import StatesGroup, State


class AnnouncementPost(StatesGroup):
    select_announcement_type = State()
    show_announcement_webapp = State()


class CreatePost(StatesGroup):
    enter_ask_for_publish = State()


class CreateAd(StatesGroup):
    enter_ad_message = State()