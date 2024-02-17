from aiogram import Router, Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

router = Router()


async def handle_create_vacancy_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]

    data = await request.post()  # application/x-www-form-urlencoded
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    return json_response({"ok": True})


async def handle_create_real_estate_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]

    data = await request.post()  # application/x-www-form-urlencoded
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    return json_response({"ok": True})


async def handle_create_vehicle_post(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]

    data = await request.post()  # application/x-www-form-urlencoded
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    return json_response({"ok": True})


async def handle_purchase(request: Request):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]

    data = await request.post()  # application/x-www-form-urlencoded
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    return json_response({"ok": True})
