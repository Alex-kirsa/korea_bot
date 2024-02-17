from aiogram.fsm.state import StatesGroup, State


class FirstStartWindow(StatesGroup):
    sub_on_channel = State()