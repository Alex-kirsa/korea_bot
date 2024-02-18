from enum import StrEnum, IntEnum


class PostStatus(IntEnum):
    """Enum for ad post statuses."""
    ACTIVE = 1
    PUBLISHED = 0
    WAIT_ACCEPT = 2
    REJECTED = 3
    STOP = 4


ad_post_status_mapping = {
    PostStatus.ACTIVE: "Ожидает публикации",
    PostStatus.PUBLISHED: "Опубликовано",
    PostStatus.WAIT_ACCEPT: "Ожидает подтверждения",
    PostStatus.REJECTED: "Отклонено",
    PostStatus.STOP: "Постинг остановлен"

}

ADS = {
    'vacancy': 'Вакансии',
    'real_estate': 'Недвижимость',
    'vehicle': 'Транспорт',
}

POST_TYPES = {
    'announcement': 'Объявления',
    'post': 'Пост',
    'ad': 'Реклама',
}


class PostTypesEnum(StrEnum):
    POST = "post"
    AD = "ad"
    ANNOUNCEMENT_VACANCY = "announcement_vacancy"
    ANNOUNCEMENT_REAL_ESTATE = "announcement_real_estate"
    ANNOUNCEMENT_VEHICLE = "announcement_vehicle"


post_types_mapping = {
    PostTypesEnum.POST: "Пост",
    PostTypesEnum.AD: "Реклама",
    PostTypesEnum.ANNOUNCEMENT_VACANCY: "Объявление; Вакансия",
    PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE: "Объявление; Недвижимость",
    PostTypesEnum.ANNOUNCEMENT_VEHICLE: "Объявление; Транспорт",
}


class TagType(StrEnum):
    """Enum for tag types."""
    VACANCY = "vacancy"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"


class BotSettingsEnum(StrEnum):
    AD_PRICE = "ad_price"
    SUB_CHANNEL_URL = "sub_channel_url"
    SUB_CHANNEL_ID = "sub_channel_id"
    WEBAPP_URL_VACANCY = "webapp_url_vacancy"
    WEBAPP_URL_REAL_ESTATE = "webapp_url_real_estate"
    WEBAPP_URL_VEHICLE = "webapp_url_vehicle"
    WEBAPP_URL_PURCHASE = 'webapp_url_purchase'
    CARD_NUMBER = 'card_number'


webapp_urls_mapping = {
    PostTypesEnum.ANNOUNCEMENT_VACANCY: BotSettingsEnum.WEBAPP_URL_VACANCY,
    PostTypesEnum.ANNOUNCEMENT_REAL_ESTATE: BotSettingsEnum.WEBAPP_URL_REAL_ESTATE,
    PostTypesEnum.ANNOUNCEMENT_VEHICLE: BotSettingsEnum.WEBAPP_URL_VEHICLE,
}
