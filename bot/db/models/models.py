from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, VARCHAR, TIMESTAMP, FLOAT, TEXT, BOOLEAN
from sqlalchemy.orm import mapped_column, Mapped, Relationship

from bot.db.base import Base
from bot.utils.constants import PostStatus, TagType, PostTypesEnum, BotSettingsEnum, PurchaseStatus


class Users(Base):
    __tablename__ = "users"

    user_id = mapped_column(BIGINT, primary_key=True)
    username = mapped_column(VARCHAR(255), nullable=True, doc='Username в Telegram', name='Username в Telegram')
    fullname = mapped_column(VARCHAR(255), nullable=False)
    rating = mapped_column(FLOAT, nullable=False, default=0)
    balance = mapped_column(FLOAT, nullable=False, default=0)
    sub_status_on_channel = mapped_column(BOOLEAN, nullable=False, default=False)

    schedule_posts: Mapped[list['SchedulePosts']] = Relationship(back_populates="user")
    top_up_operations: Mapped[list['TopUpOperations']] = Relationship(back_populates="user")
    post_messages: Mapped[list['PostMessages']] = Relationship(back_populates="user")
    ad_messages: Mapped[list['AdMessages']] = Relationship(back_populates="user")
    vacancies_posts: Mapped[list['VacanciesPosts']] = Relationship(back_populates="user")
    real_estate_posts: Mapped[list['RealEstatePosts']] = Relationship(back_populates="user")
    vehicles_posts: Mapped[list['VehiclesPosts']] = Relationship(back_populates="user")
    admins: Mapped[list['Admins']] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<Пользователь {self.fullname}> <id: {self.user_id}> <username: {self.username}>"


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = mapped_column(INTEGER, primary_key=True)
    key = mapped_column(Enum(BotSettingsEnum), nullable=False, unique=True)
    value = mapped_column(TEXT, nullable=False)


class Tags(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint('tag_type', 'tag'),  # Составное уникальное ограничение для столбцов tag_type и tag
    )

    id = mapped_column(BIGINT, primary_key=True)
    tag_type = mapped_column(Enum(TagType), nullable=False)
    tag = mapped_column(VARCHAR(50), nullable=False, index=True)

    vacancie_tag: Mapped[list['VacanciesTag']] = Relationship(back_populates="tag")
    real_estate_tag: Mapped[list['RealEstateTag']] = Relationship(back_populates="tag")
    vehicle_tag: Mapped[list['VehicleTag']] = Relationship(back_populates="tag")


class TopUpOperations(Base):
    __tablename__ = "top_up_operations"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    sender_name = mapped_column(VARCHAR(255), nullable=False)
    amount = mapped_column(INTEGER, nullable=False)
    date = mapped_column(TIMESTAMP, nullable=False)
    status = mapped_column(Enum(PurchaseStatus), nullable=False, default=PurchaseStatus.WAIT_CONFIRM)

    user: Mapped[Users] = Relationship(back_populates="top_up_operations")


class PostMessages(Base):
    __tablename__ = "post_messages"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    post_text = mapped_column(TEXT, nullable=False)

    user: Mapped[Users] = Relationship(back_populates="post_messages")


class AdMessages(Base):
    __tablename__ = "ad_messages"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    ad_text = mapped_column(TEXT, nullable=False)

    user: Mapped[Users] = Relationship(back_populates="ad_messages")


class VacanciesPosts(Base):
    __tablename__ = "vacancies_posts"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    job_type = mapped_column(VARCHAR(255), nullable=False)
    city = mapped_column(VARCHAR(255), nullable=False)
    position = mapped_column(VARCHAR(255), nullable=False)
    responsibilities = mapped_column(TEXT, nullable=False)
    korean_lang_level = mapped_column(VARCHAR(255), nullable=False)
    work_schedule_in_day = mapped_column(VARCHAR(255), nullable=False)
    work_schedule_in_week = mapped_column(VARCHAR(255), nullable=False)
    type_of_employment = mapped_column(VARCHAR(255), nullable=False)
    visa_type = mapped_column(VARCHAR(255), nullable=False)
    contact_number = mapped_column(VARCHAR(20), nullable=False)
    salary = mapped_column(VARCHAR(255), nullable=False)
    wage = mapped_column(FLOAT, nullable=False)
    text_for_publish = mapped_column(TEXT, nullable=True)
    # status = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.WAIT_ACCEPT)

    user: Mapped[Users] = Relationship(back_populates="vacancies_posts")
    tags: Mapped[list['VacanciesTag']] = Relationship(back_populates="vacancie")


class VacanciesTag(Base):
    __tablename__ = "vacancies_tag"

    id = mapped_column(BIGINT, primary_key=True)
    vacancie_id = mapped_column(BIGINT, ForeignKey(VacanciesPosts.id), nullable=False)
    tag_id = mapped_column(BIGINT, ForeignKey(Tags.id), nullable=False)

    tag: Mapped[Tags] = Relationship(back_populates="vacancie_tag")
    vacancie: Mapped[VacanciesPosts] = Relationship(back_populates="tags")


class RealEstatePosts(Base):
    __tablename__ = "real_estate_posts"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    city = mapped_column(VARCHAR(255), nullable=False)
    caption = mapped_column(VARCHAR(255), nullable=False)
    category = mapped_column(VARCHAR(255), nullable=False)
    number_of_rooms = mapped_column(VARCHAR(255), nullable=False)
    real_estate_type = mapped_column(VARCHAR(255), nullable=False)
    amenities = mapped_column(TEXT, nullable=False)
    price_for_buy = mapped_column(FLOAT, nullable=True)
    price_for_rent = mapped_column(FLOAT, nullable=True)
    pledge = mapped_column(FLOAT, nullable=True)
    announcement_from_who = mapped_column(VARCHAR(255), nullable=False)
    comment = mapped_column(TEXT, nullable=True)
    text_for_publish = mapped_column(TEXT, nullable=True)
    # status = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.WAIT_ACCEPT)

    user: Mapped[Users] = Relationship(back_populates="real_estate_posts")
    tags: Mapped[list['RealEstateTag']] = Relationship(back_populates="real_estate")


class RealEstateTag(Base):
    __tablename__ = "real_estate_tag"

    id = mapped_column(BIGINT, primary_key=True)
    real_estate_id = mapped_column(BIGINT, ForeignKey(RealEstatePosts.id), nullable=False)
    tag_id = mapped_column(BIGINT, ForeignKey(Tags.id), nullable=False)
    tag: Mapped[Tags] = Relationship(back_populates="real_estate_tag")

    real_estate: Mapped[RealEstatePosts] = Relationship(back_populates="tags")


class MediaForRealEstate(Base):
    __tablename__ = "media_for_real_estate"

    id = mapped_column(BIGINT, primary_key=True)
    real_estate_id = mapped_column(BIGINT, ForeignKey(RealEstatePosts.id), nullable=False)
    media_link = mapped_column(VARCHAR(255), nullable=False)


class VehiclesPosts(Base):
    __tablename__ = "vehicles_posts"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    city = mapped_column(VARCHAR(255), nullable=False)
    vehicle_mark = mapped_column(VARCHAR(255), nullable=False)
    vehicle_model = mapped_column(VARCHAR(255), nullable=False)
    complectaion = mapped_column(VARCHAR(255), nullable=False)
    year_of_build = mapped_column(INTEGER, nullable=False)
    engine_volume = mapped_column(VARCHAR(255), nullable=False)
    engine_power = mapped_column(VARCHAR(255), nullable=False)
    techpassport_photo = mapped_column(VARCHAR(255), nullable=False)
    date_end_technical_inspection = mapped_column(TIMESTAMP, nullable=False)
    announcement_from_who = mapped_column(VARCHAR(255), nullable=False)
    transaction_type = mapped_column(VARCHAR(255), nullable=False)
    mileage = mapped_column(VARCHAR(255), nullable=False)
    comment = mapped_column(TEXT, nullable=True)
    condition = mapped_column(VARCHAR(255), nullable=True)
    presence_of_accident = mapped_column(VARCHAR(255), nullable=True)
    text_for_publish = mapped_column(TEXT, nullable=True)
    # status = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.WAIT_ACCEPT)

    user: Mapped[Users] = Relationship(back_populates="vehicles_posts")
    tags: Mapped[list['VehicleTag']] = Relationship(back_populates="vehicle")


class VehiclePhotos(Base):
    __tablename__ = "vehicle_photos"

    id = mapped_column(BIGINT, primary_key=True)
    vehicle_id = mapped_column(BIGINT, ForeignKey(VehiclesPosts.id), nullable=False)
    photo_link = mapped_column(VARCHAR(255), nullable=False)


class VehicleTag(Base):
    __tablename__ = "vehicle_tag"

    id = mapped_column(BIGINT, primary_key=True)
    vehicle_id = mapped_column(BIGINT, ForeignKey(VehiclesPosts.id), nullable=False)
    tag_id = mapped_column(BIGINT, ForeignKey(Tags.id), nullable=False)
    tag: Mapped[Tags] = Relationship(back_populates="vehicle_tag")

    vehicle: Mapped[VehiclesPosts] = Relationship(back_populates="tags")


class SchedulePosts(Base):
    __tablename__ = "schedule_posts"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey('users.user_id'), nullable=False)
    announcement_type = mapped_column(Enum(PostTypesEnum), nullable=False)
    post_id = mapped_column(BIGINT, nullable=False)
    text_for_publish = mapped_column(TEXT, nullable=False)
    published_datetime = mapped_column(TIMESTAMP, nullable=True)
    create_date = mapped_column(TIMESTAMP, nullable=False)
    status = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.WAIT_ACCEPT)

    user: Mapped[Users] = Relationship(back_populates="schedule_posts")


class Admins(Base):
    __tablename__ = "admins"

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey(Users.user_id), nullable=False)
    login = mapped_column(VARCHAR(255), nullable=False)
    password = mapped_column(VARCHAR(255), nullable=False)
    name = mapped_column(VARCHAR(255), nullable=False)
    can_read = mapped_column(BOOLEAN, nullable=False, default=True)
    can_create = mapped_column(BOOLEAN, nullable=False, default=True)
    can_edit = mapped_column(BOOLEAN, nullable=False, default=True)
    can_delete = mapped_column(BOOLEAN, nullable=False, default=True)
    can_action_make_published = mapped_column(BOOLEAN, nullable=False, default=True)

    user: Mapped[Users] = Relationship(back_populates="admins")
