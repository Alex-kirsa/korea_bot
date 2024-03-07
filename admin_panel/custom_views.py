from typing import Any, Dict

from aiogram import Bot
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import RowActionsDisplayType, CustomView, row_action, action
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError, ActionFailed

from bot.db import Repo
from bot.db.models.models import Users
from bot.utils.constants import PostStatus, PurchaseStatus
from configreader import config


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        session: Session = request.state.session
        repo = Repo(session)
        scheduled_posts = []
        awaitng_purchases = []
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
            scheduled_posts.append(post_data)
        waiting_purchases = await repo.purchase_repo.get_purchases_with_status(status=PurchaseStatus.WAIT_CONFIRM)
        for purchase in waiting_purchases:
            user_mode = await repo.user_repo.get_user(purchase.user_id)
            purchase_data = {
                'purchase_id': purchase.id,
                'user_id': user_mode.user_id,
                'user_fullname': user_mode.fullname,
                'amount': purchase.amount,
                'status': purchase.status
            }
            awaitng_purchases.append(purchase_data)
        users_list = []
        last_10_users = await repo.user_repo.get_last_10_users_desc()
        for user in last_10_users:
            scheduled_posts_in_user = await repo.post_repo.get_scheduled_posts_in_user(user.user_id)
            user_data = {
                'user_id': user.user_id,
                'user_fullname': user.fullname,
                'post_amount': len(scheduled_posts_in_user) if scheduled_posts_in_user else 0
            }
            users_list.append(user_data)
        print(users_list)
        return templates.TemplateResponse(
            "home.html", {"request": request, "posts": scheduled_posts, 'purchases': awaitng_purchases, 'users': users_list}
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

    async def repr(self, obj: Any, request: Request) -> str:
        return f"{obj.fullname}"

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
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)


class TopUpOperation(ModelView):
    user_id: int

    page_size = 5
    page_size_options = [5, 10, 50, 100]
    actions = ['confirm_purchase_2']
    row_actions = ['view', "confirm_purchase", 'cancel_purchase']
    # exclude_fields_from_detail = ['id', 'post_id', 'published_datetime']
    # exclude_fields_from_list = ['status', 'post_id', 'published_datetime']

    row_actions_display_type = RowActionsDisplayType.ICON_LIST
    fields_default_sort = ["status"]
    label = 'Пополнения'

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Пополнение №{obj.id}"

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['status'] is None:
            errors['status'] = "Статус не может быть пустым"
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        session: Session = request.state.session
        repo = Repo(session)
        if name == 'view':
            return True
        if name == 'confirm_purchase' and request.path_params.get('pk'):
            purchase_model = await repo.purchase_repo.get_purchase(int(request.path_params.get('pk')))
            return True if purchase_model.status not in (PurchaseStatus.PAID,) else False
        elif name == 'cancel_purchase' and request.path_params.get('pk'):
            purchase_model = await repo.purchase_repo.get_purchase(int(request.path_params.get('pk')))
            return True if purchase_model.status not in (PurchaseStatus.CANCELED, PurchaseStatus.PAID,) else False
        return True

    @row_action(
        name="confirm_purchase",
        text="Подтвердить пополнение",
        confirmation="Вы уверены что хотите подтвердить это пополнение?",
        submit_btn_text="Да, подтвердить",
        submit_btn_class="btn-success",
        action_btn_class='btn-success',
        icon_class='fa fa-check-circle',
    )
    async def confirm_purchase_action(self, request: Request, pks: list[Any]) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        purchase_model = await repo.purchase_repo.get_purchase(int(pks))
        if purchase_model.status == PurchaseStatus.PAID:
            await bot.session.close()
            raise ActionFailed(f"Оплата №{len(pks)} уже подтверждена")
        await repo.user_repo.plus_user_balance(purchase_model.user_id, purchase_model.amount)
        await repo.purchase_repo.change_purchase_status(int(pks), status=PurchaseStatus.PAID)

        await bot.send_message(purchase_model.user_id, f"Оплата на сумму {purchase_model.amount} успешно подтверждена и зачислена на баланс")
        await bot.session.close()

        return f"Оплата №{len(pks)}  успешно подтверждена"

    @action(
        name="confirm_purchase_2",
        text="Подтвердить пополнение",
        confirmation="Вы уверены что хотите подтвердить это пополнение?",
        submit_btn_text="Да, подтвердить",
        submit_btn_class="btn-success",
        icon_class='fa fa-check-circle',
    )
    async def confirm_purchase_action_2(self, request: Request, pks: list[Any]) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        purchase_model = await repo.purchase_repo.get_purchase(int(pks))
        if purchase_model.status == PurchaseStatus.PAID:
            await bot.session.close()
            return ActionFailed(f"Оплата №{len(pks)} уже подтверждена")
        await repo.user_repo.plus_user_balance(purchase_model.user_id, purchase_model.amount)
        await repo.purchase_repo.change_purchase_status(int(pks), status=PurchaseStatus.PAID)
        await bot.send_message(purchase_model.user_id, f"Оплата на сумму {purchase_model.amount} успешно подтверждена и зачислена на баланс")
        await bot.session.close()

        return f"Оплата №{len(pks)}  успешно подтверждена"

    @row_action(
        name="cancel_purchase",
        text="Отменить пополнение",
        confirmation="Вы уверены что хотите отменить это пополнение?",
        submit_btn_text="Да, отменить",
        submit_btn_class="btn-danger",
        action_btn_class='btn-danger',
        icon_class='fa fa-cancel',
        form="""
            <form>
                <div class="mt-3">
                    <input  type="text" class="form-control" name="explanation" placeholder="Введите причину отмены" required>
                </div>
            </form>
            """,
    )
    async def cancel_purchase_action(self, request: Request, pks: list[Any]) -> str:
        data = await request.form()
        if not data.get('explanation'):
            raise ActionFailed('Вы не можете отменить пополнение без причины')
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        purchase_model = await repo.purchase_repo.get_purchase(int(pks))
        if purchase_model.status == PurchaseStatus.CANCELED:
            await bot.session.close()
            return ActionFailed(f"Оплата №{len(pks)} уже отклонена")
        await repo.purchase_repo.change_purchase_status(int(pks), status=PurchaseStatus.CANCELED)
        await bot.send_message(purchase_model.user_id, f"Пополнение акаунта отменено администрацией.\nПричина: {data['explanation']}")
        await bot.session.close()
        return f"Пополнение №{len(pks)} успешно отменен"

    def can_create(self, request: Request) -> bool:
        return True

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False


# class GeneralTagsView(ModelView):
#     exclude_fields_from_list = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]
#     exclude_fields_from_edit = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]
#     exclude_fields_from_detail = [Tags.id, Tags.vehicle_tag, Tags.real_estate_tag, Tags.vacancie_tag]


class VehicleTagsView(ModelView):

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['tag'] is None:
            errors['tag'] = "Тег не может быть пустым"
        if data['vehicle'] is None:
            errors['vehicle'] = "Объявление о авто не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    def can_delete(self, request: Request) -> bool:
        return False


class RealEstateTagsView(ModelView):

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['tag'] is None:
            errors['tag'] = "Тег не может быть пустым"
        if data['vehicle'] is None:
            errors['real_estate'] = "Объявление о недвижимости не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    def can_delete(self, request: Request) -> bool:
        return False


class VacanciesTagsView(ModelView):
    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['tag'] is None:
            errors['tag'] = "Тег не может быть пустым"
        if data['vacancie'] is None:
            errors['vacancie'] = "Объявление о вакансии не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    def can_delete(self, request: Request) -> bool:
        return False


class PostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status']

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Пост {obj.id}"

    async def validate(self, request: Request, data: Dict[str, Any]) -> None:
        errors: Dict[str, str] = dict()
        if data['user'] is None:
            errors['user'] = "Пользователь не может быть пустым"
        if errors:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    def can_delete(self, request: Request) -> bool:
        return False


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

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Рекламное объявление №{obj.id}"

    def can_delete(self, request: Request) -> bool:
        return False


class VacancyPostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'job_type', 'city', 'position', 'responsibilities', 'korean_lang_level',
                                'work_schedule', 'type_of_employment', 'visa_type', 'contact_number', 'salary']

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Объявление о вакансии №{obj.id}"

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

    def can_delete(self, request: Request) -> bool:
        return False


class RealEstatePostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'city', 'caption', 'category', 'number_of_rooms', 'amenities', 'price_for_buy',
                                'price_for_rent', 'pledge', 'announcement_from_who', 'comment']

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Объявление о продаже недвижимости №{obj.id}"

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

    def can_delete(self, request: Request) -> bool:
        return False


class VehiclePostView(ModelView):
    page_size = 5
    page_size_options = [5, 10, 50, 100]
    exclude_fields_from_list = ['status', 'city', 'caption', 'vehicle_mark', 'vehicle_model', 'vehicle_year',
                                'complectation', 'year_of_build', 'engine_volume', 'engine_power', 'techpassport_photo', 'date_end_technical_inspection',
                                'announcement_from_who', 'transaction_type', 'mileage', 'comment', 'condition', 'presence_of_accident']

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Объявление о продаже авто {obj.id}"

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

    def can_delete(self, request: Request) -> bool:
        return False


class SchedulePostView(ModelView):
    row_actions = ['view', "confirm_post", 'cancel_post', 'stop_posting']
    exclude_fields_from_detail = ['id', 'post_id', 'published_datetime']
    exclude_fields_from_list = ['status', 'post_id', 'published_datetime']

    async def repr(self, obj: Any, request: Request) -> str:
        return f"Запланированый пост №{obj.id}"

    async def is_row_action_allowed(self, request: Request, name: str) -> bool:
        session: Session = request.state.session
        repo = Repo(session)
        if name != 'view' and not request.path_params.get('pk'):
            return True
        if name == 'confirm_post':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params.get('pk')))
            return True if post_model.status not in (PostStatus.ACTIVE, PostStatus.PUBLISHED) else False
        elif name == 'cancel_post':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params.get('pk')))
            return True if post_model.status not in (PostStatus.REJECTED, PostStatus.PUBLISHED) else False
        elif name == 'stop_posting':
            post_model = await repo.post_repo.get_schedule_post(int(request.path_params.get('pk')))
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
        scheduled_post_model = await repo.post_repo.get_schedule_post(int(pks))
        if scheduled_post_model.status in (PostStatus.ACTIVE,):
            await bot.session.close()
            raise ActionFailed(f"Постинг поста {len(pks)} уже подтвержен")
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
        scheduled_post_model = await repo.post_repo.get_schedule_post(int(pks))
        if scheduled_post_model.status in (PostStatus.REJECTED,):
            await bot.session.close()
            raise ActionFailed(f"Постинг поста {len(pks)} уже отменен")
        ad_price = await repo.bot_settings_repo.get_bot_setting('ad_price')
        await repo.user_repo.plus_user_balance(scheduled_post_model.user_id, int(ad_price.value))
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
        scheduled_post_model = await repo.post_repo.get_schedule_post(int(pks))
        if scheduled_post_model.status in (PostStatus.STOP,):
            await bot.session.close()
            raise ActionFailed(f"Постинг поста {len(pks)} уже остановлен")
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
