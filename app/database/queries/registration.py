from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.models import Registration, User, Event  # импортируйте ваши модели

# Добавление регистрации на событие с автоопределением очереди
async def orm_add_registration(
    session: AsyncSession,
    user_id: UUID,
    event: Event,  # Передаем объект Event, а не просто ID
    payment_status: str = "unpaid"
):
    """
    Добавление новой регистрации на событие с автоматическим определением позиции в очереди.
    Если есть места - ставит 0 (подтвержденная регистрация).
    Если мест нет - добавляет в очередь с соответствующей позицией.
    """
    # Получаем актуальную информацию о событии
    # Проверяем, есть ли свободные места
    available_spots = event.max_participants - event.participants
    
    if available_spots > 0:
        # Есть свободные места - подтвержденная регистрация
        status = "confirmed"
        queue_position = 0  # 0 означает подтвержденную регистрацию
        
        # Увеличиваем счетчик участников в событии
        await orm_increment_participants(session, event.id)
    else:
        # Нет мест - ставим в очередь
        status = "pending"
        # Получаем следующую позицию в очереди
        queue_position = await orm_get_next_queue_position(session, event.id)
    
    session.add(Registration(
        user_id=user_id,
        event_id=event.id,
        status=status,
        payment_status=payment_status,
        queue_position=queue_position
    ))
    await session.commit()
    
    # Возвращаем созданную регистрацию и информацию о том, в очередь или нет
    return {
        "status": status,
        "queue_position": queue_position,
        "is_confirmed": status == "confirmed"
    }

# Проверка наличия регистрации
async def orm_check_registration(
    session: AsyncSession, 
    user_id: UUID, 
    event_id: int
):
    """
    Проверка, зарегистрирован ли пользователь на событие
    """
    query = select(Registration).where(
        and_(
            Registration.user_id == user_id,
            Registration.event_id == event_id
        )
    )
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True


async def orm_get_registrations(session: AsyncSession):
    """
    Получение всех регистраций
    """
    query = select(Registration)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_registration(session: AsyncSession, registration_id: int):
    """
    Получение регистрации по её ID
    """
    query = select(Registration).where(Registration.id == registration_id)
    result = await session.execute(query)
    return result.scalar()

# Получение регистрации по пользователю и событию
async def orm_get_registration_by_user_and_event(
    session: AsyncSession, 
    user_id: UUID, 
    event_id: int
):
    """
    Получение регистрации конкретного пользователя на конкретное событие
    """
    query = select(Registration).where(
        and_(
            Registration.user_id == user_id,
            Registration.event_id == event_id
        )
    )
    result = await session.execute(query)
    return result.scalar()

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

# Вспомогательный метод для уменьшения счетчика участников
async def orm_decrement_participants(session: AsyncSession, event_id: int):
    """
    Уменьшение количества участников события на 1
    """
    query = update(Event).where(Event.id == event_id).values(
        participants=Event.participants - 1
    )
    await session.execute(query)
    await session.commit()

# Получение следующей позиции в очереди
async def orm_get_next_queue_position(session: AsyncSession, event_id: int):
    """
    Получение следующей доступной позиции в очереди на событие
    """
    query = select(func.max(Registration.queue_position)).where(
        and_(
            Registration.event_id == event_id,
            Registration.queue_position > 0  # Только позиции в очереди (не 0)
        )
    )
    result = await session.execute(query)
    max_position = result.scalar()
    
    if max_position is None:
        return 1
    return max_position + 1

# Подтверждение регистрации из очереди
async def orm_confirm_from_queue(session: AsyncSession, registration_id: int):
    """
    Подтверждение регистрации из очереди (когда освободилось место)
    """
    # Получаем регистрацию
    registration = await orm_get_registration(session, registration_id)
    if not registration or registration.status != "pending":
        return False
    
    # Обновляем статус и позицию
    query = update(Registration).where(Registration.id == registration_id).values(
        status="confirmed",
        queue_position=0
    )
    await session.execute(query)
    
    # Увеличиваем счетчик участников в событии
    await orm_increment_participants(session, registration.event_id)
    
    await session.commit()
    return True

# Отмена регистрации
async def orm_cancel_registration(session: AsyncSession, registration_id: int):
    """
    Отмена регистрации. Если это была подтвержденная регистрация,
    освобождает место и может подтвердить следующего в очереди
    """
    # Получаем регистрацию
    registration = await orm_get_registration(session, registration_id)
    if not registration:
        return False
    
    event_id = registration.event_id
    was_confirmed = registration.status == "confirmed"
    
    # Обновляем статус на отмененный
    query = update(Registration).where(Registration.id == registration_id).values(
        status="cancelled",
        queue_position=-1  # -1 для отмененных регистраций
    )
    await session.execute(query)
    
    # Если это была подтвержденная регистрация, уменьшаем счетчик участников
    if was_confirmed:
        await orm_decrement_participants(session, event_id)
        
        # Проверяем, есть ли кто-то в очереди
        next_in_queue = await orm_get_next_in_queue(session, event_id)
        if next_in_queue:
            # Подтверждаем следующего в очереди
            await orm_confirm_from_queue(session, next_in_queue.id)
    
    await session.commit()
    return True

# Получение следующего в очереди
async def orm_get_next_in_queue(session: AsyncSession, event_id: int):
    """
    Получение следующей регистрации в очереди (с наименьшей положительной позицией)
    """
    query = select(Registration).where(
        and_(
            Registration.event_id == event_id,
            Registration.status == "pending",
            Registration.queue_position > 0
        )
    ).order_by(Registration.queue_position).limit(1)
    
    result = await session.execute(query)
    return result.scalar()

# Получение всех регистраций с информацией о статусе
async def orm_get_event_registrations_with_status(session: AsyncSession, event_id: int):
    """
    Получение всех регистраций на событие с разделением на подтвержденные и в очереди
    """
    # Подтвержденные регистрации (queue_position = 0)
    confirmed_query = select(Registration).where(
        and_(
            Registration.event_id == event_id,
            Registration.status == "confirmed",
            Registration.queue_position == 0
        )
    ).order_by(Registration.id)
    confirmed = await session.execute(confirmed_query)
    
    # В очереди (queue_position > 0)
    queue_query = select(Registration).where(
        and_(
            Registration.event_id == event_id,
            Registration.status == "pending",
            Registration.queue_position > 0
        )
    ).order_by(Registration.queue_position)
    queue = await session.execute(queue_query)
    
    return {
        "confirmed": confirmed.scalars().all(),
        "queue": queue.scalars().all()
    }

# Получение позиции пользователя в очереди
async def orm_get_user_queue_position(session: AsyncSession, user_id: UUID, event_id: int):
    """
    Получение позиции пользователя в очереди на событие
    Возвращает 0 если пользователь подтвержден, -1 если не в очереди,
    и положительное число если в очереди
    """
    registration = await orm_get_registration_by_user_and_event(session, user_id, event_id)
    
    if not registration:
        return -1  # Не зарегистрирован
    
    if registration.status == "confirmed":
        return 0  # Подтвержден
    
    if registration.status == "pending" and registration.queue_position > 0:
        return registration.queue_position  # В очереди
    
    return -1  # Другой статус

# Проверка, может ли пользователь зарегистрироваться
async def orm_can_register(session: AsyncSession, user_id: UUID, event: Event):
    """
    Проверка, может ли пользователь зарегистрироваться на событие
    """
    # Проверяем, не зарегистрирован ли уже
    existing = await orm_check_registration(session, user_id, event.id)
    if existing:
        return False, "already_registered"
    
    # Проверяем, есть ли места
    if event.participants < event.max_participants:
        return True, "confirmed"
    else:
        return True, "queue"  # Можно в очередь

# Статистика по регистрациям с учетом очереди
async def orm_get_detailed_event_stats(session: AsyncSession, event: Event):
    """
    Детальная статистика по регистрациям на событие
    """
    # Получаем все регистрации
    registrations = await orm_get_event_registrations_with_status(session, event.id)
    
    confirmed_count = len(registrations["confirmed"])
    queue_count = len(registrations["queue"])
    
    # Информация о местах
    total_spots = event.max_participants
    occupied_spots = event.participants
    available_spots = total_spots - occupied_spots
    
    # Проверка, заполнено ли событие
    is_full = occupied_spots >= total_spots
    
    return {
        "event_id": event.id,
        "event_title": event.title,
        "total_spots": total_spots,
        "occupied_spots": occupied_spots,
        "available_spots": available_spots,
        "is_full": is_full,
        "confirmed_registrations": confirmed_count,
        "queue_length": queue_count,
        "total_registrations": confirmed_count + queue_count
    }



