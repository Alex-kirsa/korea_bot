from aiogram_i18n import I18nContext

from bot.db.models.models import VacanciesPosts, VacanciesTag, VehiclesPosts, VehicleTag, RealEstatePosts, RealEstateTag


async def generate_vacancy_text(i18n: I18nContext, vacancy: VacanciesPosts, vacancy_tags: list[VacanciesTag]) -> str:
    text = i18n.get('vacancy_template_msg',
                    position=vacancy.position,
                    city=vacancy.city,
                    tags="".join([f"#{tag.tag} " for tag in vacancy_tags]),
                    wage=vacancy.wage,
                    salary=vacancy.salary,
                    job_type=vacancy.job_type,
                    responsibilities=vacancy.responsibilities,
                    korean_level='' if not vacancy.korean_level else i18n.get('korean_level', korean_level=vacancy.korean_level) + '\n',
                    visa_type='' if not vacancy.visa_type else i18n.get('visa_type', visa_type=vacancy.visa_type) + '\n',
                    type_of_employment=vacancy.type_of_employment,
                    work_schedule_day=vacancy.work_schedule_in_day,
                    work_schedule_week=vacancy.work_schedule_in_week,
                    contact_number=vacancy.contact_number,
                    )
    return text


async def generate_vehicle_text(i18n: I18nContext, vehicle: VehiclesPosts, vehicle_tags: list[VehicleTag]) -> str:
    sell_type = vehicle.transaction_type
    sell_type_mapping = {
        'Продажа': 'sell',
        'В рассрочку': 'sell_installments',
        'В кредит': 'sell_credit',
        'Обмен': 'trade',
    }
    sell_type_text = i18n.get(sell_type_mapping[sell_type], mark=vehicle.vehicle_mark, model=vehicle.vehicle_model) + '\n'
    text = i18n.get('vehicle_template_msg',
                    sell_type=sell_type_text,
                    tags="".join([f"#{tag.tag} " for tag in vehicle_tags]),
                    year=vehicle.year,
                    engine_volume=vehicle.mileage,
                    engine_power=vehicle.engine,
                    milage=vehicle.mileage,
                    condition=vehicle.condition,
                    presence_of_accident="Есть" if vehicle.presence_of_accident else "Нет",
                    city=vehicle.city,
                    date_end_technical_inspection=vehicle.date_end_technical_inspection,
                    comment=vehicle.comment,
                    announcement_from_who=vehicle.announcement_from_who
                    )
    return text


async def generate_real_estate_text(i18n: I18nContext, real_estate: RealEstatePosts, real_estate_tags: list[RealEstateTag]) -> str:
    real_estate_type = real_estate.real_estate_type
    category = real_estate.category
    category_mapping = {
        'Продам': 'real_estate_sell_type',
        'Аренда помесячно': 'real_estate_rent_per_month_type',
        'Длительная аренда': 'real_estate_rent_long_time',
        'Посуточная аренда': 'real_estate_rent_per_day',
    }
    price = real_estate.price_for_rent if "aренда" in str(category).lower() else real_estate.price_for_buy
    rent_type_msg = i18n.get(category_mapping[category], real_estate_type=real_estate_type, city=real_estate.city) + '\n'
    text = i18n.get('real_estate_template_msg',
                    rent_type=rent_type_msg,
                    tags="".join([f"#{tag.tag} " for tag in real_estate_tags]),
                    caption=real_estate.caption,
                    rooms_amount=real_estate.rooms_amount,
                    amenities=real_estate.amenities,
                    price=price,
                    pledge_text=i18n.get('pledge', pledge=real_estate.pledge) + '\n' if real_estate.pledge else '',
                    comment=real_estate.comment,
                    announcement_from_who=real_estate.announcement_from_who
                    )
    return text
