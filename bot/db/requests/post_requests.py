import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.models import *


class PostRequestsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_user_post(self, user_id: int, status: PostStatus = None):
        query = select(SchedulePosts).where(SchedulePosts.user_id == user_id).order_by(SchedulePosts.id.desc())
        if status:
            query = select(SchedulePosts).where(SchedulePosts.user_id == user_id, SchedulePosts.status == status).order_by(SchedulePosts.id.desc())
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

    async def add_scheduled_post(self, user_id: int, post_id: int, announcement_type: PostTypesEnum, text_for_publish: str, status: str = PostStatus.ACTIVE):
        query = SchedulePosts(user_id=user_id, post_id=post_id, announcement_type=announcement_type,
                              text_for_publish=text_for_publish, status=status,
                              create_date=datetime.datetime.now())
        self.session.add(query)
        await self.session.commit()
        await self.session.flush()

    async def get_scheduled_post_created_last_24_hours(self, user_id: int, announcement_type: list[PostTypesEnum] = None):
        query = select(SchedulePosts).where(SchedulePosts.user_id == user_id, SchedulePosts.create_date >= datetime.datetime.now() - datetime.timedelta(days=1),
                                            SchedulePosts.announcement_type.in_(announcement_type))
        result = await self.session.execute(query)
        return result.scalars().all()

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

    async def get_scheduled_posts_in_user(self, user_id: int):
        query = select(SchedulePosts).where(SchedulePosts.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_vacancie_post(self, user_id: int, json_data: dict):
        stmt = VacanciesPosts(
            user_id=user_id,
            job_type=json_data['jobType']['name'],
            city=json_data['city'],
            position=json_data['position'],
            responsibilities=json_data['duties'],
            korean_lang_level=json_data['koreanLevel'],
            work_schedule_in_day=json_data['dailySchedule'],
            work_schedule_in_week=json_data['weeklySchedule'],
            type_of_employment=json_data['employmentStatus'],
            visa_type=json_data['visaType'],
            contact_number=json_data['contactNumber'],
            salary=json_data['salaryType']['name'],
            wage=int(json_data['salary'])
        )
        self.session.add(stmt)
        await self.session.commit()
        await self.session.flush()
        return stmt

    async def get_tag(self, tag_id: int):
        query = select(Tags).where(Tags.id == tag_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def add_vacancies_tags(self, tags_list: list[VacanciesTag]):
        self.session.add_all(tags_list)
        await self.session.commit()
        await self.session.flush()

    async def update_vacancy_post_text(self, vacancy_id: int, post_text):
        query = update(VacanciesPosts).where(VacanciesPosts.id == vacancy_id).values(text_for_publish=post_text)
        await self.session.execute(query)
        await self.session.commit()

    async def add_real_estate_post(self, user_id: int, json_data: dict):
        stmt = RealEstatePosts(
            user_id=user_id,
            city=json_data['city'],
            caption=json_data['name'],
            category=json_data['category']['name'],
            number_of_rooms=json_data['roomsQuantity']['name'],
            real_estate_type=json_data['housingType']['name'],
            amenities=json_data['facilities'].capitalize(),
            price_for_buy=int(json_data['price']) if json_data['category']['name'] == 'Продажа' else None,
            price_for_rent=int(json_data['price']) if json_data['category']['name'] != 'Продажа' else None,
            pledge=int(json_data['deposit']),
            announcement_from_who=json_data['publisherType']['name'].capitalize(),
            comment=json_data.get('comment')
        )
        self.session.add(stmt)
        await self.session.commit()
        await self.session.flush()
        return stmt

    async def add_real_estate_tags(self, tags_list: list[RealEstateTag]):
        self.session.add_all(tags_list)
        await self.session.commit()
        await self.session.flush()

    async def update_real_estate_text(self, real_estate_id: int, post_text):
        query = update(RealEstatePosts).where(RealEstatePosts.id == real_estate_id).values(text_for_publish=post_text)
        await self.session.execute(query)
        await self.session.commit()

    async def add_real_estate_media(self, media_list: list[MediaForRealEstate]):
        self.session.add_all(media_list)
        await self.session.commit()
        await self.session.flush()

    async def add_vehicle_post(self, user_id: int, json_data: dict):
        stmt = VehiclesPosts(
            user_id=user_id,
            city=json_data['city'],
            vehicle_mark=json_data['brand'],
            vehicle_model=json_data['model'],
            complectaion=json_data['trim'],
            year_of_build=int(json_data['yearOfManufacture']),
            engine_volume=json_data['engineVolume'],
            engine_power=json_data['enginePower'],
            techpassport_photo=json_data['registrationDocumentPhoto'][0],
            date_end_technical_inspection=datetime.datetime.strptime(json_data['inspectionEndDate'], '%d.%m.%Y %H:%M'),
            announcement_from_who=json_data['advertiserType']['name'].capitalize(),
            transaction_type=json_data['dealType']['name'].capitalize(),
            mileage=json_data['mileage'],
            comment=json_data.get('comment'),
            condition=json_data.get('condition'),
            presence_of_accident=json_data['accidentHistory']['name'].capitalize() if json_data.get('accidentHistory') else None,
        )
        self.session.add(stmt)
        await self.session.commit()
        await self.session.flush()
        return stmt

    async def add_vehicle_tags(self, tags_list: list[VehicleTag]):
        self.session.add_all(tags_list)
        await self.session.commit()
        await self.session.flush()

    async def update_vehicle_text(self, vehicle_post_id: int, post_text):
        query = update(VehiclesPosts).where(VehiclesPosts.id == vehicle_post_id).values(text_for_publish=post_text)
        await self.session.execute(query)
        await self.session.commit()

    async def add_vehicle_media(self, media_list: list[VehiclePhotos]):
        self.session.add_all(media_list)
        await self.session.commit()
        await self.session.flush()
