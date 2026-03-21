from typing import Optional
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, time
from app.database.models import Event, Registration  # импортируйте вашу модель

# Добавление события
async def orm_add_event(
    session: AsyncSession,
    title: str,
    section: str,
    description: str,
    participation_conditions: str,
    location: str,
    start_datetime: datetime,
    timezone: str,
    price: float,
    max_participants: int,
    participants: int = 0,
    status: str = "active"
):
    """
    Добавление нового события
    """
    session.add(Event(
        title=title,
        section=section,
        description=description,
        participation_conditions=participation_conditions,
        location=location,
        start_datetime=start_datetime,
        timezone=timezone,
        price=price,
        max_participants=max_participants,
        participants=participants,
        status=status
    ))
    await session.commit()

# Получение всех событий
async def orm_get_events(
    session: AsyncSession,
    page: Optional[int] = None,
    size: Optional[int] = None,
):
    """
    Получение всех событий
    """
    query = select(Event)
    result = await session.execute(query)
    if size and page != None:
        min_offset = size * page
        max_offset = size * page + size
        return result.scalars().all()[min_offset:max_offset]
    else:
        return result.scalars().all()


async def orm_count_events(session: AsyncSession) -> int:
    """Считает общее количество событий (для пагинации)."""
    query = select(func.count()).select_from(Event)
    result = await session.execute(query)
    return int(result.scalar_one())


def _get_date_range(date_filter: Optional[str]) -> tuple[datetime, datetime] | None:
    """Строит диапазон дат по фильтру из UI (локальное время сервера)."""
    if not date_filter:
        return None

    now = datetime.now()
    today = now.date()

    if date_filter == "today":
        start_dt = datetime.combine(today, time.min)
        end_dt = datetime.combine(today, time.max)
        return start_dt, end_dt

    if date_filter == "tomorrow":
        tomorrow = today + timedelta(days=1)
        start_dt = datetime.combine(tomorrow, time.min)
        end_dt = datetime.combine(tomorrow, time.max)
        return start_dt, end_dt

    if date_filter == "week":
        start_dt = datetime.combine(today, time.min)
        end_dt = start_dt + timedelta(days=7) - timedelta(seconds=1)
        return start_dt, end_dt

    if date_filter == "month":
        first_day = datetime(now.year, now.month, 1)
        # первый день следующего месяца
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        end_dt = next_month - timedelta(seconds=1)
        return first_day, end_dt

    if date_filter == "next-month":
        # вычисляем первый/последний день следующего месяца
        if now.month == 12:
            next_month_first = datetime(now.year + 1, 1, 1)
        else:
            next_month_first = datetime(now.year, now.month + 1, 1)

        if next_month_first.month == 12:
            following_month_first = datetime(next_month_first.year + 1, 1, 1)
        else:
            following_month_first = datetime(next_month_first.year, next_month_first.month + 1, 1)

        end_dt = following_month_first - timedelta(seconds=1)
        return next_month_first, end_dt

    return None


def _build_event_conditions(
    *,
    search: Optional[str] = None,
    date_filter: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    price_filter: Optional[str] = None,
):
    conditions = []

    if search:
        conditions.append(Event.title.ilike(f"%{search}%"))

    date_range = _get_date_range(date_filter)
    if date_range:
        start_dt, end_dt = date_range
        conditions.append(Event.start_datetime >= start_dt)
        conditions.append(Event.start_datetime <= end_dt)

    if section:
        conditions.append(Event.section == section)

    if status:
        conditions.append(Event.status == status)

    if price_filter == "free":
        conditions.append(Event.price == 0)
    elif price_filter == "paid":
        conditions.append(Event.price > 0)

    return conditions


async def orm_get_events_filtered(
    session: AsyncSession,
    *,
    page: int,
    size: int,
    search: Optional[str] = None,
    date_filter: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    price_filter: Optional[str] = None,
):
    conditions = _build_event_conditions(
        search=search,
        date_filter=date_filter,
        section=section,
        status=status,
        price_filter=price_filter,
    )

    query = select(Event)
    if conditions:
        query = query.where(and_(*conditions))

    query = query.order_by(Event.start_datetime).offset(page * size).limit(size)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_count_events_filtered(
    session: AsyncSession,
    *,
    search: Optional[str] = None,
    date_filter: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    price_filter: Optional[str] = None,
):
    conditions = _build_event_conditions(
        search=search,
        date_filter=date_filter,
        section=section,
        status=status,
        price_filter=price_filter,
    )

    query = select(func.count()).select_from(Event)
    if conditions:
        query = query.where(and_(*conditions))

    result = await session.execute(query)
    return int(result.scalar_one())


# Получение одного события по ID
async def orm_get_event(session: AsyncSession, event_id: int):
    """
    Получение события по его ID
    """
    query = select(Event).where(Event.id == event_id)
    result = await session.execute(query)
    return result.scalar()

# Получение активных событий
async def orm_get_active_events(session: AsyncSession):
    """
    Получение всех активных событий
    """
    query = select(Event).where(Event.status == "active")
    result = await session.execute(query)
    return result.scalars().all()

# Получение предстоящих событий
async def orm_get_upcoming_events(session: AsyncSession):
    """
    Получение предстоящих событий (дата начала > текущего времени)
    """
    query = select(Event).where(
        and_(
            Event.start_datetime > datetime.now(),
            Event.status == "active"
        )
    ).order_by(Event.start_datetime)
    result = await session.execute(query)
    return result.scalars().all()

# Получение событий с доступными местами
async def orm_get_events_with_available_spots(session: AsyncSession):
    """
    Получение событий, где есть свободные места
    """
    query = select(Event).where(
        and_(
            Event.participants < Event.max_participants,
            Event.status == "active"
        )
    )
    result = await session.execute(query)
    return result.scalars().all()

# Обновление события
async def orm_update_event(session: AsyncSession, event_id: int, data: dict):
    """
    Обновление информации о событии
    data может содержать: title, description, participation_conditions, lacation,
    start_datetime, timezone, price, max_participants, status
    """
    query = update(Event).where(Event.id == event_id).values(**data)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount > 0

# Добавление участника на событие
async def orm_add_participant(session: AsyncSession, event_id: int):
    """
    Увеличение количества участников события на 1
    """
    # Сначала получаем текущее событие
    event = await orm_get_event(session, event_id)
    if event and event.participants < event.max_participants:
        query = update(Event).where(Event.id == event_id).values(
            participants=Event.participants + 1
        )
        await session.execute(query)
        await session.commit()
        return True
    return False

# Удаление участника с события
async def orm_remove_participant(session: AsyncSession, event_id: int):
    """
    Уменьшение количества участников события на 1
    """
    event = await orm_get_event(session, event_id)
    if event and event.participants > 0:
        query = update(Event).where(Event.id == event_id).values(
            participants=Event.participants - 1
        )
        await session.execute(query)
        await session.commit()
        return True
    return False

# Обновление статуса события
async def orm_change_event_status(session: AsyncSession, event_id: int, status: str):
    """
    Изменение статуса события (active, cancelled, completed, postponed)
    """
    query = update(Event).where(Event.id == event_id).values(
        status=status
    )
    await session.execute(query)
    await session.commit()

# Удаление события
async def orm_delete_event(session: AsyncSession, event_id: int):
    """
    Безопасное удаление события по ТЗ:
    - платное мероприятие НЕ удаляем физически, переводим в cancelled
    - бесплатное удаляем физически
    """
    event = await orm_get_event(session, event_id)
    if not event:
        return {"status": "not_found", "message": "Event not found"}

    # Платные события только отменяем, чтобы сохранить данные для возвратов.
    if float(event.price) > 0:
        await orm_change_event_status(session, event_id, "cancelled")
        return {
            "status": "cancelled",
            "message": "Платное мероприятие переведено в статус 'cancelled'. Данные для возвратов сохранены.",
        }

    # Для бесплатных — удаляем регистрации и само событие.
    await session.execute(delete(Registration).where(Registration.event_id == event_id))
    await session.execute(delete(Event).where(Event.id == event_id))
    await session.commit()

    return {
        "status": "deleted",
        "message": "Бесплатное мероприятие удалено.",
    }

# Проверка наличия события
async def orm_check_event(session: AsyncSession, event_id: int):
    """
    Проверка существования события по ID
    """
    query = select(Event).where(Event.id == event_id)
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Проверка доступности мест на событии
async def orm_check_availability(session: AsyncSession, event_id: int):
    """
    Проверка, есть ли свободные места на событии
    """
    query = select(Event).where(
        and_(
            Event.id == event_id,
            Event.participants < Event.max_participants
        )
    )
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Получение количества свободных мест
async def orm_get_available_spots(session: AsyncSession, event_id: int):
    """
    Получение количества свободных мест на событии
    """
    event = await orm_get_event(session, event_id)
    if event:
        return event.max_participants - event.participants
    return 0

# Поиск событий по локации
async def orm_get_events_by_location(session: AsyncSession, location: str):
    """
    Получение событий по локации
    """
    query = select(Event).where(Event.location.ilike(f"%{location}%"))
    result = await session.execute(query)
    return result.scalars().all()

# Поиск событий по дате
async def orm_get_events_by_date_range(
    session: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
):
    """
    Получение событий в указанном диапазоне дат
    """
    query = select(Event).where(
        and_(
            Event.start_datetime >= start_date,
            Event.start_datetime <= end_date
        )
    ).order_by(Event.start_datetime)
    result = await session.execute(query)
    return result.scalars().all()

# Получение событий с сортировкой по цене
async def orm_get_events_sorted_by_price(session: AsyncSession, ascending: bool = True):
    """
    Получение всех событий, отсортированных по цене
    """
    query = select(Event)
    if ascending:
        query = query.order_by(Event.price)
    else:
        query = query.order_by(Event.price.desc())
    
    result = await session.execute(query)
    return result.scalars().all()

# Вспомогательный метод для увеличения счетчика участников
async def orm_increment_participants(session: AsyncSession, event_id: int):
    """
    Увеличение количества участников события на 1
    """
    query = update(Event).where(Event.id == event_id).values(
        participants=Event.participants + 1
    )
    await session.execute(query)
    await session.commit()

