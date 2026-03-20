from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(Integer())
    username: Mapped[str] = mapped_column(String(50))
    full_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer(), default=0)
    section_id: Mapped[int] = mapped_column(Integer(), default=1)
    last_event: Mapped[DateTime] = mapped_column(DateTime(), default=None, nullable=True)
    is_blacklist: Mapped[bool] = mapped_column(Boolean, default=False)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    super_user: Mapped[bool] = mapped_column(Boolean(), default=False)
    
    # Права доступа к разделам
    events: Mapped[str] = mapped_column(String(25), default="forbidden")
    registers: Mapped[str] = mapped_column(String(25), default="forbidden")
    partners_apply: Mapped[str] = mapped_column(String(25), default="forbidden")
    exhibitions_apply: Mapped[str] = mapped_column(String(25), default="forbidden")
    users: Mapped[str] = mapped_column(String(25), default="forbidden")
    queue: Mapped[str] = mapped_column(String(25), default="forbidden")
    payments: Mapped[str] = mapped_column(String(25), default="forbidden")
    documents: Mapped[str] = mapped_column(String(25), default="forbidden")
    reviews: Mapped[str] = mapped_column(String(25), default="forbidden")
    notifications: Mapped[str] = mapped_column(String(25), default="forbidden")
    support: Mapped[str] = mapped_column(String(25), default="forbidden")
    qr_codes: Mapped[str] = mapped_column(String(25), default="forbidden")


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    # Раздел мероприятия: business / family (Клуб молодых семей)
    section: Mapped[str] = mapped_column(String(25), default="business")
    description: Mapped[str] = mapped_column(Text())
    participation_conditions: Mapped[str] = mapped_column(Text())
    location: Mapped[str] = mapped_column(String(100))
    start_datetime: Mapped[DateTime] = mapped_column(DateTime())
    timezone: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Numeric())
    max_participants: Mapped[int] = mapped_column(Integer())
    participants: Mapped[int] = mapped_column(Integer())
    status: Mapped[str] = mapped_column(String(20))


class Registration(Base):
    __tablename__ = 'registrations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='RESTRICT'), nullable=False)
    status: Mapped[str] = mapped_column(String(25))
    payment_status: Mapped[str] = mapped_column(String(25))
    queue_position: Mapped[int] = mapped_column(Integer())

    users: Mapped['User'] = relationship(backref='registrations')
    events: Mapped['Event'] = relationship(backref='registrations')


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'))
    registration_id: Mapped[int] = mapped_column(ForeignKey('registrations.id', ondelete='CASCADE'))
    amount: Mapped[float] = mapped_column(Numeric())
    status: Mapped[str] = mapped_column(String(25))
    payment_id: Mapped[int] = mapped_column(Integer())

    users: Mapped['User'] = relationship(backref='payments')
    events: Mapped['Event'] = relationship(backref='payments')


class PartnerApplication(Base):
    __tablename__ = 'partner_aplication'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    direction: Mapped[str] = mapped_column(String(50))
    cooperation_format: Mapped[str] = mapped_column(String(50))
    benefit_description: Mapped[str] = mapped_column(Text())
    comment: Mapped[str] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(25))
    admin_notes: Mapped[str] = mapped_column(String(100))

    users: Mapped['User'] = relationship(backref='partner_aplication')


class ExhibitionApplications(Base):
    __tablename__ = 'exhibition_applications'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    legal_status: Mapped[str] = mapped_column(String(10))
    company_name: Mapped[str] = mapped_column(String(50))
    contact_person: Mapped[str] = mapped_column(String(50))
    activity_description: Mapped[str] = mapped_column(Text())
    provided_type: Mapped[str] = mapped_column(String(25))
    need_support: Mapped[bool] = mapped_column(Boolean())
    full_price: Mapped[float] = mapped_column(Numeric(), nullable=True) # Полная стоимость
    support_amount: Mapped[float] = mapped_column(Numeric(), nullable=True) # Сумма поддержки
    full_amount: Mapped[float] = mapped_column(Numeric(), nullable=True) # Сумма к оплате
    payment_status: Mapped[str] = mapped_column(String(25))
    status: Mapped[str] = mapped_column(String(25)) # Статус заявки (new / reviewing / approved / rejected / paid)

    users: Mapped['User'] = relationship(backref='exhibition_applications')
    




    


