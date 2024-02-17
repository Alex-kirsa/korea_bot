from enum import StrEnum, IntEnum


class AdPostStatus(IntEnum):
    """Enum for ad post statuses."""
    ACTIVE = 1
    PUBLISHED = 0
    WAIT_ACCEPT = 2
    REJECTED = 3
    STOP = 4


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
