from aiogram import Router
from .start import router as start_router
from .user_handlers import router as user_router


def include_handlers(router: Router):
    router.include_routers(start_router, user_router)

