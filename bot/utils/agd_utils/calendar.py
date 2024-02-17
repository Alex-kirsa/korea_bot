import datetime
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarConfig, CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarScopeView, CalendarDaysView, DATE_TEXT, TODAY_TEXT, CalendarMonthView, CalendarYearsView
from aiogram_dialog.widgets.text import Text, Format
from aiogram_i18n import I18nContext
from babel.dates import get_day_names, get_month_names
from pytz import tzinfo

SELECTED_DAYS_KEY = "selected_dates"


calendar_config = CalendarConfig(
    min_date=datetime.date.today(),
)


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        locale = manager.middleware_data['i18n'].locale
        return get_day_names(
            width="short", context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: datetime.date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        i18n: I18nContext = manager.middleware_data['i18n']
        locale = i18n.locale
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay("🔴", DATE_TEXT),
                today_text=MarkedDay("⭕", TODAY_TEXT),
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }
