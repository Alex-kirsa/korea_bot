import asyncio
import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Repo
from bot.utils.constants import PostTypesEnum, PostStatus, BotSettingsEnum


async def send_schedule_message(ctx):
    db_factory = ctx["db_factory"]
    bot: Bot = ctx["bot"]
    async with db_factory() as db_session:
        session: AsyncSession = db_session
        repo = Repo(session)
        posts_for_publish = await repo.post_repo.get_posts_for_publish()
        if not posts_for_publish:
            return
        channel_id = await repo.bot_settings_repo.get_bot_setting(BotSettingsEnum.SUB_CHANNEL_ID)
        for post in posts_for_publish:
            post_type = post.announcement_type
            message_for_owner_mapping = {
                PostTypesEnum.POST: f"✅Ваш пост #{post.id} опубликован в канале",
                PostTypesEnum.AD: f"✅Ваша реклама #{post.id} опубликована в канале",
                PostTypesEnum.ANNOUNCEMENT_VACANCY: f"✅Ваша вакансия #{post.id} опубликована в канале",
                PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE: f"✅Ваша недвижемость #{post.id} опубликована в канале",
                PostTypesEnum.ANNOUNCEMENT_VEHICLE: f"✅Ваше сообщение #{post.id}, о продаже авто, опубликована в канале",
            }
            message = post.text_for_publish
            await bot.send_message(chat_id=int(channel_id.value), text=message, disable_web_page_preview=True)
            await bot.send_message(chat_id=post.user_id, text=message_for_owner_mapping[post_type] + "\n")
            await repo.post_repo.update_schedule_post_status(post.id, PostStatus.PUBLISHED)
            await repo.post_repo.update_schedule_published_datetime(post.post_id, datetime.datetime.now())
            await asyncio.sleep(45)
