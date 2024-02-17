import asyncio

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import Repo
from bot.utils.constants import PostTypesEnum, AdPostStatus


async def send_schedule_message(ctx):
    db_factory = ctx["db_factory"]
    bot: Bot = ctx["bot"]
    async with db_factory() as db_session:
        session: AsyncSession = db_session
        repo = Repo(session)
        posts_for_publish = await repo.post_repo.get_posts_for_publish()
        if not posts_for_publish:
            return
        for post in posts_for_publish:
            post_type = post.announcement_type
            if post_type == PostTypesEnum.POST:
                post_model = await repo.post_repo.get_post(post.post_id)
                message = post_model.post_text
                message_for_owner = "✅Ваш пост опубликован в канале"
            elif post_type == PostTypesEnum.AD:
                ad_model = await repo.post_repo.get_ad_post(post.post_id)
                message = ad_model.ad_text
                message_for_owner = "✅Ваша реклама опубликована в канале"
            elif post_type == PostTypesEnum.ANNOUNCEMENT_VACANCY:
                ...
                message_for_owner = "✅Ваша вакансия опубликована в канале"

            elif post_type == PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE:
                ...
                message_for_owner = "✅Ваша недвижемость опубликована в канале"

            elif post_type == PostTypesEnum.ANNOUNCEMENT_VEHICLE:
                ...
                message_for_owner = "✅Ваше сообщение, о продаже авто, опубликована в канале"

            else:
                continue
            await bot.send_message(chat_id=post.user_id, text=message_for_owner + "\n")
            await repo.post_repo.update_schedule_post_status(post.id, AdPostStatus.PUBLISHED)
            await asyncio.sleep(60)
