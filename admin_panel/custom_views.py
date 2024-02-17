import json
from typing import Any, Dict

from jinja2 import Template
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import RowActionsDisplayType, CustomView
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError

from bot.db import Repo
from bot.db.models.models import AdMessages, SchedulePosts, Users
from bot.utils.constants import PostTypesEnum


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
    fields_default_sort = ["fullname"]
    row_actions_display_type = RowActionsDisplayType.ICON_LIST

    async def select2_selection(self, obj: Any, request: Request) -> str:
        template_str = "<span>{{obj.fullname}}</span>"
        return Template(template_str, autoescape=True).render(obj=obj)

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


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        session: Session = request.state.session
        repo = Repo(session)
        schedule_posts = []
        schedule_posts_raw = await repo.post_repo.get_all_posts_desc()
        for schedule_post in schedule_posts_raw:
            user_mode = await repo.user_repo.get_user(schedule_post.user_id)
            post_type = schedule_post.announcement_type
            if post_type == PostTypesEnum.POST:
                post_model = await repo.post_repo.get_post(schedule_post.post_id)
                post_text = post_model.post_text
            elif post_type == PostTypesEnum.AD:
                ad_model = await repo.post_repo.get_ad_post(schedule_post.post_id)
                post_text = ad_model.ad_text
            elif post_type == PostTypesEnum.ANNOUNCEMENT_VACANCY:
                vacancy_model = await repo.post_repo.get_vacancy_post(schedule_post.post_id)
                post_text = ...
            elif post_type == PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE:
                real_estate_model = await repo.post_repo.get_real_estate_post(schedule_post.post_id)
                post_text = ...
            elif post_type == PostTypesEnum.ANNOUNCEMENT_VEHICLE:
                vehicle_model = await repo.post_repo.get_vehicle_post(schedule_post.post_id)
                post_text = ...
            else:
                continue
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


class SchedulePostView(ModelView):

    def can_create(self, request: Request) -> bool:
        return True

    def can_edit(self, request: Request) -> bool:
        return True

    def can_delete(self, request: Request) -> bool:
        return False

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['status'] is None:
            errors['status'] = "Статус не может быть пустым"
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)


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
