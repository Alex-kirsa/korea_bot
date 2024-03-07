import os.path

import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_admin import I18nConfig, DropDown
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.i18n import SUPPORTED_LOCALES

from admin_panel.custom_views import UserView, AdminView, BotSettingsView, HomeView, SchedulePostView, VehiclePostView, RealEstatePostView, VacancyPostView, AdPostView, PostView, \
    TopUpOperation, VacanciesTagsView, RealEstateTagsView, VehicleTagsView
from admin_panel.provider import MyAuthProvider
from admin_panel.requests import confirm_post
from bot.db.models import models
from configreader import config

engine = create_async_engine(str(config.postgredsn), future=True, echo=False)

static_dir = os.path.join('admin_panel', 'static')


def main():
    db_pool = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    app = Starlette(
        routes=[
            Mount(
                "/static", app=StaticFiles(directory=static_dir), name="static"
            ),
            Route(
                "/admin/confirm-post", confirm_post, methods=["GET", "POST"]
            )

        ],
    )
    # Create admin
    admin = Admin(
        engine,
        title="Админка Korean Bot",
        base_url="/",
        statics_dir=static_dir,
        templates_dir=f"{static_dir}",
        login_logo_url="admin/static/korea_flag.png",  # base_url + '/statics/' + path_to_the_file
        index_view=HomeView(label="Home", icon="fa fa-home"),
        auth_provider=MyAuthProvider(allow_routes=[f"{static_dir}/korea_flag.png"], db_pool=db_pool),
        middlewares=[Middleware(SessionMiddleware, secret_key=config.webhook_secret)],
        i18n_config=I18nConfig(default_locale="ru", language_switcher=SUPPORTED_LOCALES)
    )
    admin.add_view(UserView(models.Users, label='Пользователи', name='пользователи', icon='fa fa-address-book'))
    admin.add_view(AdminView(models.Admins, label='Администраторы', name='администраторы', icon='fa fa-user-secret'))
    admin.add_view(TopUpOperation(models.TopUpOperations, name='пополнения', icon='fa fa-credit-card-alt'))
    admin.add_view(
        DropDown(
            'Теги',
            icon="fa fa-tags",
            always_open=False,
            views=[
                ModelView(models.Tags, label='Общие теги', name='теги', icon="fa fa-tags"),
                VehicleTagsView(models.VehicleTag, label='Теги транспорта', name='теги транспорта', icon="fa fa-car"),
                RealEstateTagsView(models.RealEstateTag, label='Теги недвижимости', name='теги недвижимости', icon="fa fa-building"),
                VacanciesTagsView(models.VacanciesTag, label='Теги вакансий', name='теги вакансий', icon="fa fa-briefcase"),

            ]
        )
    )
    admin.add_view(
        DropDown(
            'Посты',
            icon="fa fa-book",
            always_open=False,
            views=[
                PostView(models.PostMessages, label='Простые посты', name='посты', icon='fa fa-question'),
                AdPostView(models.AdMessages, label='Реклама', name='объявления', icon='fa fa-usd'),
                VacancyPostView(models.VacanciesPosts, label='Вакансии', name='вакансии', icon='fa fa-briefcase'),
                RealEstatePostView(models.RealEstatePosts, label='Недвижимость', name='недвижимость', icon='fa fa-building'),
                VehiclePostView(models.VehiclesPosts, label='Транспорт', name='транспорт', icon='fa fa-car')
            ]
        )
    )

    admin.add_view(SchedulePostView(models.SchedulePosts, label='Запланированые посты', name='запланированые посты', icon='fa fa-calendar'))
    admin.add_view(BotSettingsView(models.BotSettings, label='Настройки бота', name='настройки бота', icon='fa fa-cogs'))
    admin.mount_to(app)
    return app


if __name__ == "__main__":
    # asyncio.run(init_db())
    uvicorn.run(main, port=config.admin_panel_port, host=config.admin_panel_host, log_level='info', factory=True)
