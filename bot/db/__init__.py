from sqlalchemy.ext.asyncio import AsyncSession

from .requests.post_requests import PostRequestsRepo
from .requests.user_requests import UserRequestsRepo
from .requests.bot_settings import BotSettingsRepo


class Repo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRequestsRepo(session)
        self.bot_settings_repo = BotSettingsRepo(session)
        self.post_repo = PostRequestsRepo(session)
