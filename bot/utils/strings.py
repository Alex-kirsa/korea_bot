from aiogram_i18n.cores import FluentRuntimeCore

from bot.db.models.models import VacanciesPosts, VacanciesTag, VehiclesPosts, VehicleTag, RealEstatePosts, RealEstateTag


async def generate_vacancy_text(i18n_core: FluentRuntimeCore, vacancy: VacanciesPosts, vacancy_tags: list[VacanciesTag]) -> str:
    korean_level = '' if not vacancy.korean_lang_level else i18n_core.get('korean_level', 'uk', korean_level=vacancy.korean_lang_level) + '\n'
    visa_type = '' if not vacancy.visa_type else i18n_core.get('visa_type', 'uk', visa_type=vacancy.visa_type) + '\n'
    text = i18n_core.get('vacancy_template_msg',
                         'uk',
                         position=vacancy.position,
                         city=vacancy.city,
                         tags="".join([f"#{tag.tag.tag} " for tag in vacancy_tags]),
                         wage=vacancy.wage,
                         salary=vacancy.salary,
                         job_type=vacancy.job_type,
                         responsibilities=vacancy.responsibilities,
                         korean_level=korean_level,
                         visa_type=visa_type,
                         type_of_employment=vacancy.type_of_employment,
                         work_schedule_day=vacancy.work_schedule_in_day,
                         work_schedule_week=vacancy.work_schedule_in_week,
                         contact_number=vacancy.contact_number,
                         )
    return text


async def generate_real_estate_text(i18n: FluentRuntimeCore, real_estate: RealEstatePosts, real_estate_tags: list[RealEstateTag]) -> str:
    real_estate_type = real_estate.real_estate_type
    if str(real_estate_type).lower() == 'студия':
        real_estate_type = 'студию'
    category = real_estate.category
    category_mapping = {
        'Продажа': 'real_estate_sell_type',
        'Аренда': 'real_estate_rent',
        'Помесячно': 'real_estate_rent_per_month_type',
        'Длительная Аренда': 'real_estate_rent_long_time',
        'Суточная Аренда': 'real_estate_rent_per_day',
    }
    price = real_estate.price_for_buy if "Продажа" == category else real_estate.price_for_rent
    rent_type_msg = i18n.get(category_mapping[category], 'uk', real_estate_type=real_estate_type, city=real_estate.city) + '\n'
    text = i18n.get('real_estate_template_msg', 'uk',
                    rent_type=rent_type_msg,
                    tags="".join([f"#{tag.tag.tag} " for tag in real_estate_tags]) if real_estate_tags else '',
                    caption=real_estate.caption,
                    rooms_amount=str(real_estate.number_of_rooms).upper(),
                    amenities=real_estate.amenities,
                    price=price,
                    pledge_text=i18n.get('pledge_text', 'uk', pledge=real_estate.pledge) + '\n' if real_estate.pledge else '',
                    comment=real_estate.comment if real_estate.comment else '',
                    announcement_from_who=real_estate.announcement_from_who
                    )
    return text


async def generate_vehicle_text(i18n: FluentRuntimeCore, vehicle: VehiclesPosts, vehicle_tags: list[VehicleTag]) -> str:
    sell_type = vehicle.transaction_type
    sell_type_mapping = {
        'В рассрочку': 'sell_installments',
        'В кредит': 'sell_credit',
        'Обмен': 'trade',
        'Полная стоимость': 'sell',
    }
    sell_type_text = i18n.get(sell_type_mapping[sell_type], 'uk', mark=vehicle.vehicle_mark, model=vehicle.vehicle_model) + '\n'
    text = i18n.get('vehicle_template_msg', 'uk',
                    sell_type=sell_type_text,
                    tags="".join([f"#{tag.tag.tag} " for tag in vehicle_tags]),
                    year=vehicle.year_of_build,
                    engine_volume=vehicle.engine_volume,
                    engine_power=vehicle.engine_power,
                    milage=vehicle.mileage,
                    condition=vehicle.condition,
                    presence_of_accident=vehicle.presence_of_accident,
                    city=vehicle.city,
                    date_end_technical_inspection=vehicle.date_end_technical_inspection.strftime('%d.%m.%Y %H:%M'),
                    comment=vehicle.comment,
                    announcement_from_who=vehicle.announcement_from_who
                    )
    return text
