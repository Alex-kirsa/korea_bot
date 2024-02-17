from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from bot.db import Repo
from configreader import config

users = {
    "root": {
        "name": "Administrator",
        "avatar": "korea_flag.png",
        "company_logo_url": "korea_flag.png",
        "roles": ["read", "create", "edit", "delete", "action_make_published", 'root']
    },
}


class MyAuthProvider(AuthProvider):
    """
    This is for demo purpose, it's not a better
    way to save and validate user credentials
    """

    def __init__(self,
                 db_pool: async_sessionmaker[AsyncSession],
                 login_path: str = "/login",
                 logout_path: str = "/logout",
                 allow_paths: Optional[Sequence[str]] = None,
                 allow_routes: Optional[Sequence[str]] = None
                 ):
        self.db_pool = db_pool
        self.login_path = login_path
        self.logout_path = logout_path
        self.allow_paths = allow_paths
        self.allow_routes = allow_routes
        super().__init__()

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        if len(username) < 3:
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )
        async with self.db_pool() as session:
            repo = Repo(session)
            admin_model = await repo.user_repo.get_admin_with_login_and_password(username, password)
            if admin_model:
                request.session.update({"username": username})
                return response
            elif username in users and password == config.admin_panel_password:
                request.session.update({"username": username})
                return response

            raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        async with self.db_pool() as session:
            repo = Repo(session)
            admin_model = await repo.user_repo.get_admin_by_login(request.session.get("username", None))
            if request.session.get("username", None) in users:
                """
                Save current `user` object in the request state. Can be used later
                to restrict access to connected user.
                """
                request.state.user = users.get(request.session["username"])
                return True
            elif admin_model:
                user_data = {
                    "name": admin_model.name,
                    "avatar": "avatar.png",
                    "company_logo_url": "logo-icon-2.png",
                    'roles': []
                }

                if admin_model.can_read:
                    user_data['roles'].append("read")
                if admin_model.can_create:
                    user_data['roles'].append("create")
                if admin_model.can_edit:
                    user_data['roles'].append("edit")
                if admin_model.can_delete:
                    user_data['roles'].append("delete")
                if admin_model.can_action_make_published:
                    user_data['roles'].append("action_make_published")
                request.state.user = user_data
                return True

        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user["name"] + "!"
        # Update logo url according to current_user
        custom_logo_url = None
        if user.get("company_logo_url", None):
            custom_logo_url = request.url_for("static", path=user["company_logo_url"])
        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        photo_url = None
        if user["avatar"] is not None:
            photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username=user["name"], photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
