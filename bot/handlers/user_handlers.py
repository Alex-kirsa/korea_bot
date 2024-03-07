import datetime
import logging
import os

from aiogram import Router, Bot
from aiogram_dialog import BgManagerFactory, ShowMode
from aiogram_i18n.cores import FluentRuntimeCore
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Repo
from bot.db.models.models import VacanciesTag, RealEstateTag, MediaForRealEstate, VehicleTag, VehiclePhotos
from bot.utils.constants import PostStatus, PostTypesEnum
from bot.utils.strings import generate_vacancy_text, generate_real_estate_text, generate_vehicle_text

router = Router()


async def handle_create_vacancy_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]
    dialogs_factory: BgManagerFactory = request.app["dialogs_factory"]
    path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
    core: FluentRuntimeCore = request.app["core"]
    await core.startup()
    json_data = await request.json()
    user_id = int(json_data["tg_user_id"])

    # Создаем объект VacanciesPosts
    async with db_factory() as session:
        session: AsyncSession
        repo: Repo = Repo(session=session)
        vacancie_model = await repo.post_repo.add_vacancie_post(user_id, json_data)
        tags_list = []
        # Создаем объекты VacanciesTag и добавляем их в сессию
        for tag in json_data['tags']:
            tag_model = await repo.post_repo.get_tag(tag['id'])
            tags_list.append(
                VacanciesTag(
                    vacancie_id=vacancie_model.id,
                    tag_id=tag_model.id,
                    tag=tag_model
                )
            )
        await repo.post_repo.add_vacancies_tags(tags_list)
        text = await generate_vacancy_text(core, vacancie_model, tags_list)
        await repo.post_repo.update_vacancy_post_text(vacancie_model.id, text)
        await repo.post_repo.add_scheduled_post(user_id=user_id, post_id=vacancie_model.id,
                                                announcement_type=PostTypesEnum.ANNOUNCEMENT_VACANCY, text_for_publish=text,
                                                status=PostStatus.ACTIVE)
    await bot.send_message(user_id, core.get('you_in_query', 'uk'))
    await dialogs_factory.bg(bot, user_id, user_id).done(show_mode=ShowMode.DELETE_AND_SEND)
    return json_response({"ok": True})


async def handle_create_real_estate_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]
    dialogs_factory: BgManagerFactory = request.app["dialogs_factory"]
    core: FluentRuntimeCore = request.app["core"]
    await core.startup()
    json_data = await request.json()
    print(json_data)
    user_id = int(json_data["tg_user_id"])

    async with db_factory() as session:
        session: AsyncSession
        repo: Repo = Repo(session=session)
        real_estate_model = await repo.post_repo.add_real_estate_post(user_id, json_data)
        tags_list = []
        # Создаем объекты VacanciesTag и добавляем их в сессию
        if json_data.get('tags'):
            for tag in json_data['tags']:
                tag_model = await repo.post_repo.get_tag(tag['id'])
                tags_list.append(
                    RealEstateTag(
                        real_estate_id=real_estate_model.id,
                        tag_id=tag_model.id,
                        tag=tag_model
                    )
                )
            await repo.post_repo.add_real_estate_tags(tags_list)
        if json_data.get('media'):
            media_list = [MediaForRealEstate(
                real_estate_id=real_estate_model.id,
                media_link=media
            )
                for media in json_data['media']]
            await repo.post_repo.add_real_estate_media(media_list)
        text = await generate_real_estate_text(core, real_estate_model, tags_list)
        await repo.post_repo.update_real_estate_text(real_estate_model.id, text)
        await repo.post_repo.add_scheduled_post(user_id=user_id, post_id=real_estate_model.id,
                                                announcement_type=PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE,
                                                text_for_publish=text,
                                                status=PostStatus.ACTIVE)
    await bot.send_message(user_id, core.get('you_in_query', 'uk'))
    await dialogs_factory.bg(bot, user_id, user_id).done(show_mode=ShowMode.DELETE_AND_SEND)
    return json_response({"ok": True})


async def handle_create_vehicle_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]
    dialogs_factory: BgManagerFactory = request.app["dialogs_factory"]
    core: FluentRuntimeCore = request.app["core"]
    await core.startup()
    json_data = await request.json()
    print(json_data)

    user_id = int(json_data["tg_user_id"])
    async with db_factory() as session:
        session: AsyncSession
        repo: Repo = Repo(session=session)
        vehicle_post_model = await repo.post_repo.add_vehicle_post(user_id, json_data)
        tags_list = []
        # Создаем объекты VacanciesTag и добавляем их в сессию
        if json_data.get('tags'):
            for tag in json_data['tags']:
                tag_model = await repo.post_repo.get_tag(tag['id'])
                if not tag_model:
                    continue
                tags_list.append(
                    VehicleTag(
                        vehicle_id=vehicle_post_model.id,
                        tag_id=tag_model.id,
                        tag=tag_model
                    )
                )
            await repo.post_repo.add_vehicle_tags(tags_list)
        if json_data.get('media'):
            media_list = [
                VehiclePhotos(
                    vehicle_id=vehicle_post_model.id,
                    photo_link=media
                )
                for media in json_data['media']
            ]
            await repo.post_repo.add_vehicle_media(media_list)
        text = await generate_vehicle_text(core, vehicle_post_model, tags_list)
        await repo.post_repo.update_vehicle_text(vehicle_post_model.id, text)
        await repo.post_repo.add_scheduled_post(user_id=user_id, post_id=vehicle_post_model.id,
                                                announcement_type=PostTypesEnum.ANNOUNCEMENT_VEHICLE,
                                                text_for_publish=text,
                                                status=PostStatus.ACTIVE)
    await bot.send_message(user_id, core.get('you_in_query', 'uk'))
    await dialogs_factory.bg(bot, user_id, user_id).done(show_mode=ShowMode.DELETE_AND_SEND)
    return json_response({"ok": True})


async def handle_purchase(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]
    dialogs_factory: BgManagerFactory = request.app["dialogs_factory"]
    core: FluentRuntimeCore = request.app["core"]
    await core.startup()
    json_data = await request.json()
    user_id = int(json_data["tg_user_id"])
    async with db_factory() as session:
        session: AsyncSession
        repo: Repo = Repo(session=session)
        await repo.purchase_repo.add_purchase(user_id, json_data['name'], int(json_data['sum']), datetime.datetime.strptime(json_data['date'], '%d.%m.%Y %H:%M'))
        await bot.send_message(user_id, core.get('request_topup_sended', 'uk'))
        await dialogs_factory.bg(bot, user_id, user_id).done(show_mode=ShowMode.DELETE_AND_SEND)
    return json_response({"ok": True})
