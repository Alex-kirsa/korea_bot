from aiogram.filters import Filter
from aiogram.types import ChatMemberUpdated

from configreader import config


class AddBotFilter(Filter):
    async def __call__(self, update: ChatMemberUpdated) -> bool:
        return (
            update.new_chat_member.user.id == int(config.bot_token.split(":")[0])
            and str(update.new_chat_member.status) == "ChatMemberStatus.ADMINISTRATOR"
        )
