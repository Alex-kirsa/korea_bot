from aiogram.fsm.state import StatesGroup, State


class MainMenu(StatesGroup):
    select_action = State()


class UserAccount(StatesGroup):
    show_account_info = State()


class TopUpBalance(StatesGroup):
    enter_amount = State()


class UserPostRequests(StatesGroup):
    show_user_requests = State()
    show_post_details = State()


class ShowPost(StatesGroup):
    show_post_text = State()


class UpdatePostText(StatesGroup):
    enter_text = State()
