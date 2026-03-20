from typing import Optional
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database.models import Event  # импортируйте вашу модель

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
    await session.execute(query)
    await session.commit()

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
    Удаление события
    """
    query = delete(Event).where(Event.id == event_id)
    await session.execute(query)
    await session.commit()

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

