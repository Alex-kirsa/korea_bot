# from typing import Callable, Awaitable, Dict, Any

# from aiocache import RedisCache
# from aiogram import BaseMiddleware
# from aiogram.types import TelegramObject

# from bot.utils.redis.redis_requests import CacheRepo


# class RedisCacheMiddleware(BaseMiddleware):
#     def __init__(self, cache: RedisCache):
#         super().__init__()
#         self.cache = cache

#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any],
#     ) -> Any:
#         data["cache"] = CacheRepo(self.cache, data["bot"].id)
#         return await handler(event, data)
