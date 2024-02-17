from typing import Any, Awaitable, Callable, Dict, Optional, Union

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from aiogram_i18n import I18nContext, I18nMiddleware
from aiogram_i18n.cores import BaseCore
from aiogram_i18n.managers import BaseManager
from fluent.runtime import FluentLocalization
from redis.asyncio import Redis

from configreader import config


class I18nDialogMiddleware(BaseMiddleware):
    def __init__(
        self,
        l10ns: Dict[str, FluentLocalization],
        default_lang: str,
        i18n_format_key: str = config.i18n_format_key,
    ):
        super().__init__()
        self.l10ns = l10ns
        self.default_lang = default_lang

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]],
            Awaitable[Any],
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        # some language/locale retrieving logic
        lang = 'uk'

        l10n = self.l10ns[lang]
        # we use fluent.runtime here, but you can create custom functions

        data[config.i18n_format_key] = l10n.format_value
        return await handler(event, data)


class RedisI18nMiddleware(I18nMiddleware):
    def __init__(
        self,
        core: BaseCore[Any],
        redis: Redis,
        manager: Optional[BaseManager] = None,
        context_key: str = "i18n",
        locale_key: Optional[str] = None,
        middleware_key: str = "i18n_middleware",
        default_locale: str = "uk",
        key_separator: str = "-",
    ) -> None:
        super().__init__(
            core,
            manager,
            context_key,
            locale_key,
            middleware_key,
            default_locale,
            key_separator,
        )
        self.redis = redis
        self.default_locale = default_locale

    def setup(self, dispatcher: Dispatcher) -> None:
        dispatcher.update.outer_middleware.register(self)
        dispatcher.startup.register(self.core.startup)
        dispatcher.shutdown.register(self.core.shutdown)
        dispatcher.startup.register(self.manager.startup)
        dispatcher.shutdown.register(self.manager.shutdown)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        locale = 'uk'
        data[self.context_key] = context = I18nContext(
            locale=locale,
            core=self.core,
            manager=self.manager,
            data=data,
            key_separator=self.key_separator,
        )
        if self.locale_key is not None:
            data[self.locale_key] = locale
        data[self.middleware_key] = self

        I18nContext.set_current(context)
        return await handler(event, data)
