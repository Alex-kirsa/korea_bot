import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.models import *


class PostRequestsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_user_post(self, user_id: int, status: PostStatus = None):
        query = select(SchedulePosts).where(SchedulePosts.user_id == user_id)
        if status:
            query = select(SchedulePosts).where(SchedulePosts.user_id == user_id, SchedulePosts.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_post(self, user_id: int, post_text: str):
        query = PostMessages(user_id=user_id, post_text=post_text)
        self.session.add(query)
        await self.session.commit()
        await self.session.flush()
        return query.id

    async def add_ad_post(self, user_id: int, post_text: str):
        query = AdMessages(user_id=user_id, ad_text=post_text)
        self.session.add(query)
        await self.session.commit()
        await self.session.flush()
        return query.id

    async def add_scheduled_post(self, user_id: int, post_id: int, announcement_type: PostTypesEnum, text_for_publish: str):
        query = SchedulePosts(user_id=user_id, post_id=post_id, announcement_type=announcement_type, text_for_publish=text_for_publish)
        self.session.add(query)
        await self.session.commit()
        await self.session.flush()

    async def get_schedule_post(self, schedule_post_id: int):
        query = select(SchedulePosts).where(SchedulePosts.id == schedule_post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_tags(self, tag_type: str):
        query = select(Tags).where(Tags.tag_type == tag_type)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_posts_for_publish(self):
        query = select(SchedulePosts).where(SchedulePosts.status == PostStatus.ACTIVE)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_posts_desc(self, status: PostStatus = None):
        query = select(SchedulePosts).order_by(SchedulePosts.id.desc())
        if status:
            query = select(SchedulePosts).where(SchedulePosts.status == status).order_by(SchedulePosts.id.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_post(self, post_id: int):
        query = select(PostMessages).where(PostMessages.id == post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_ad_post(self, ad_post_id: int):
        query = select(AdMessages).where(AdMessages.id == ad_post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_schedule_post_status(self, schedule_post_id: int, status: PostStatus):
        query = update(SchedulePosts).where(SchedulePosts.id == schedule_post_id).values(status=status)
        await self.session.execute(query)
        await self.session.commit()

    async def get_vacancy_post(self, post_id: int):
        query = select(VacanciesPosts).where(VacanciesPosts.id == post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_real_estate_post(self, post_id: int):
        query = select(RealEstatePosts).where(RealEstatePosts.id == post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_vehicle_post(self, post_id: int):
        query = select(VehiclesPosts).where(VehiclesPosts.id == post_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_schedule_published_datetime(self, post_id: int, published_datetime: datetime):
        query = update(SchedulePosts).where(SchedulePosts.id == post_id).values(published_datetime=published_datetime)
        await self.session.execute(query)
        await self.session.commit()

    async def update_schedule_post_text(self, post_id: int, text_for_publish: str):
        query = update(SchedulePosts).where(SchedulePosts.id == post_id).values(text_for_publish=text_for_publish)
        await self.session.execute(query)
        await self.session.commit()

    async def update_post_text(self, post_id: int, post_text: str):
        query = update(PostMessages).where(PostMessages.id == post_id).values(post_text=post_text)
        await self.session.execute(query)
        await self.session.commit()

    async def update_ad_text(self, ad_post_id: int, ad_text: str):
        query = update(AdMessages).where(AdMessages.id == ad_post_id).values(ad_text=ad_text)
        await self.session.execute(query)
        await self.session.commit()