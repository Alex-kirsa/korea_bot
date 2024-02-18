from typing import Any, Dict

from aiogram import Bot
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import RowActionsDisplayType, CustomView, row_action
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError, ActionFailed

from bot.db import Repo
from bot.db.models.models import Users, Tags
from bot.utils.constants import PostTypesEnum, PostStatus
from configreader import config


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        session: Session = request.state.session
        repo = Repo(session)
        schedule_posts = []
        schedule_posts_raw = await repo.post_repo.get_all_posts_desc(status=PostStatus.WAIT_ACCEPT)
        for schedule_post in schedule_posts_raw:
            user_mode = await repo.user_repo.get_user(schedule_post.user_id)
            post_type = schedule_post.announcement_type
            post_text = schedule_post.text_for_publish
            post_data = {
                'post_id': schedule_post.id,
                'user_id': user_mode.user_id,
                'user_fullname': user_mode.fullname,
                'post_text': post_text,
                'status': schedule_post.status
            }
            schedule_posts.append(post_data)
        return templates.TemplateResponse(
            "home.html", {"request": request, "posts": schedule_posts}
        )


class UserView(ModelView):
    page_size = 5

    page_size_options = [5, 10, 50, 100, -1]
    pk_attr = True
    exclude_fields_from_list = [
        Users.real_estate_posts,
        Users.vacancies_posts,
        Users.vehicles_posts,
        Users.ad_messages,
        Users.post_messages,
        Users.schedule_posts,
        Users.top_up_operations,
        Users.sub_status_on_channel
    ]
    exclude_fields_from_edit = [
        Users.username,
        Users.real_estate_posts,
        Users.vacancies_posts,
        Users.vehicles_posts,
        Users.ad_messages,
        Users.post_messages,
        Users.schedule_posts,
        Users.top_up_operations,
        Users.sub_status_on_channel
    ]
    fields_default_sort = ["fullname"]
    row_actions_display_type = RowActionsDisplayType.ICON_LIST

    # async def select2_selection(self, obj: Any, request: Request) -> str:
    #     print(obj)
    #     template_str = "<span>{{obj.fullname}}</span>"
    #     return Template(template_str, autoescape=True).render(obj=obj)

    def can_delete(self, request: Request) -> bool:
        return False

    def can_create(self, request: Request) -> bool:
        return False


class AdminView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]

    exclude_fields_from_list = ["id", 'user_id']
    row_actions_display_type = RowActionsDisplayType.DROPDOWN

    # def is_accessible(self, request: Request) -> bool:
    #     print(request.state.user)
    #     return ["root", 'admin'] in request.state.user["roles"]

    def can_delete(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    def can_create(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    def can_edit(self, request: Request) -> bool:
        return 'can_edit' and 'root' in request.state.user['roles']

    def can_view_details(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
            raise FormValidationError(errors)
        return await super().validate(request, data)


class TopUpOperation(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]

    row_actions_display_type = RowActionsDisplayType.ICON_LIST
    fields_default_sort = ["amount"]
    label = 'Пополнения'

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False


class GeneralTagsView(ModelView):
    exclude_fields_from_list = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]
    exclude_fields_from_edit = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]
    exclude_fields_from_detail = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]


class PostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class AdPostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class VacancyPostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'job_type', 'city', 'position', 'responsibilities', 'korean_lang_level',
                                'work_schedule', 'type_of_employment', 'visa_type', 'contact_number', 'salary']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['status'] is None:
            errors['status'] = "Статус не может быть пустым"
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if data['tags'] is None:
            errors['tags'] = "Нужен хотя бы один тег"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class RealEstatePostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'city', 'caption', 'category', 'number_of_rooms', 'amenities', 'price_for_buy',
                                'price_for_rent', 'pledge', 'announcement_from_who', 'comment']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['status'] is None:
            errors['status'] = "Статус не может быть пустым"
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if data['tags'] is None:
            errors['tags'] = "Нужен хотя бы один тег"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class VehiclePostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'city', 'caption', 'vehicle_mark', 'vehicle_model', 'vehicle_year',
                                'complectation', 'year_of_build', 'engine_volume', 'engine_power', 'techpassport_photo', 'date_end_technical_inspection',
                                'announcement_from_who', 'transaction_type', 'mileage', 'comment', 'condition', 'presence_of_accident']

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['status'] is None:
            errors['status'] = "Статус не может быть пустым"
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if data['tags'] is None:
            errors['tags'] = "Нужен хотя бы один тег"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class SchedulePostView(ModelView):
    row_actions = ['view', "confirm_post", 'cancel_post', 'stop_posting']
    exclude_fields_from_detail = ['id', 'post_id', 'published_datetime']
    exclude_fields_from_list = ['status', 'post_id', 'published_datetime']

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        session: Session = request.state.session
        repo = Repo(session)
        if name != 'view' and not request.path_params.get('pk'):
            return True
        if name == 'confirm_post':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params['pk']))
            return True if post_model.status not in (PostStatus.ACTIVE, PostStatus.PUBLISHED) else False
        elif name == 'cancel_post':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params['pk']))
            return True if post_model.status not in (PostStatus.REJECTED, PostStatus.PUBLISHED) else False
        elif name == 'stop_posting':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params['pk']))
            return False if post_model.status is PostStatus.STOP else True
        return True

    @row_action(
        name="confirm_post",
        text="Подтвердить публикацию",
        confirmation="Вы уверены что хотите подтвердить эту публикацию?",
        submit_btn_text="Да, подтвердить",
        submit_btn_class="btn-success",
        action_btn_class='btn-success',
        icon_class='fa fa-check-circle',
    )
    async def confirm_post_action(self, request: Request, pks: list[Any]) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        await repo.post_repo.update_schedule_post_status(int(pks), PostStatus.ACTIVE)
        post_model = await repo.post_repo.get_schedule_post(int(pks))
        await bot.send_message(post_model.user_id, f"Вы в очереди. Ваш пост будет опубликован на течении 15 минут.")
        await bot.session.close()

        return f"{len(pks)} пост успешно подтвержден"

    @row_action(
        name="cancel_post",
        text="Отменить публикацию",
        confirmation="Вы уверены что хотите отменить эту публикацию?",
        submit_btn_text="Да, подтвердить",
        submit_btn_class="btn-danger",
        action_btn_class='btn-danger',
        icon_class='fa fa-cancel',
        form="""
            <form>
                <div class="mt-3">
                    <input  type="text" class="form-control" name="explanation" placeholder="Введите причину отказа" required>
                </div>
            </form>
            """,
    )
    async def cancel_post_action(self, request: Request, pks: list[Any]) -> str:
        data = await request.form()
        if not data.get('explanation'):
            raise ActionFailed('Вы не можете отменить пост без причины')
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        await repo.post_repo.update_schedule_post_status(int(pks), PostStatus.REJECTED)
        post_model = await repo.post_repo.get_schedule_post(int(pks))
        await bot.send_message(post_model.user_id, f"Ваш пост отменен администрацией.\nПричина: {data['explanation']}")
        await bot.session.close()
        return f"{len(pks)} пост успешно отменен"

    @row_action(
        name="stop_posting",
        text="Поставить публикацию на паузу",
        confirmation="Вы уверены что хотите остановить постинг этой публикации?",
        submit_btn_text="Да, остановить",
        submit_btn_class="btn-warning",
        action_btn_class='btn-warning',
        icon_class='fa fa-stop-circle',
        form="""
                <form>
                    <div class="mt-3">
                        <input  type="text" class="form-control" name="explanation" placeholder="Введите причину остановки" required>
                    </div>
                </form>
                """,
    )
    async def stop_posting_action(self, request: Request, pks: list[Any]) -> str:
        data = await request.form()
        if not data.get('explanation'):
            raise ActionFailed('Вы не можете остановить пост без причины')
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        await repo.post_repo.update_schedule_post_status(int(pks), PostStatus.STOP)
        post_model = await repo.post_repo.get_schedule_post(int(pks))
        await bot.send_message(post_model.user_id, f"<b>Ваш пост остановлен администрацией.</b>\nПричина: <i>{data['explanation']}</i>")
        await bot.session.close()
        return f"Постинг поста {len(pks)} успешно остановлен"

    def can_create(self, request: Request) -> bool:
        return True

    def can_edit(self, request: Request) -> bool:
        return True

    def can_delete(self, request: Request) -> bool:
        return False


class BotSettingsView(ModelView):
    page_size = 10
    page_size_options = [5, 10, 50, 100]

    exclude_fields_from_list = ["id"]
    row_actions_display_type = RowActionsDisplayType.DROPDOWN

    def is_accessible(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    def can_delete(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    def can_create(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    def can_edit(self, request: Request) -> bool:
        return 'root' in request.state.user['roles']

    # def can_view_details(self, request: Request) -> bool:
    #     return 'root' in request.state.user['roles']
