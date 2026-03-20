from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from app.database.models import Payment, User, Event, Registration  # импортируйте ваши модели

# Добавление платежа
async def orm_add_payment(
    session: AsyncSession,
    user_id: UUID,
    event_id: int,
    registration_id: int,
    amount: float,
    payment_id: int,
    status: str = "pending"
):
    """
    Добавление нового платежа
    """
    session.add(Payment(
        user_id=user_id,
        event_id=event_id,
        registration_id=registration_id,
        amount=amount,
        payment_id=payment_id,
        status=status
    ))
    await session.commit()

# Получение всех платежей
async def orm_get_payments(session: AsyncSession):
    """
    Получение всех платежей
    """
    query = select(Payment)
    result = await session.execute(query)
    return result.scalars().all()

# Получение одного платежа по ID
async def orm_get_payment(session: AsyncSession, payment_id: int):
    """
    Получение платежа по его ID
    """
    query = select(Payment).where(Payment.id == payment_id)
    result = await session.execute(query)
    return result.scalar()

# Получение платежа по payment_id (внешний ID платежной системы)
async def orm_get_payment_by_payment_id(session: AsyncSession, payment_id: int):
    """
    Получение платежа по payment_id (внешний ID платежной системы)
    """
    query = select(Payment).where(Payment.payment_id == payment_id)
    result = await session.execute(query)
    return result.scalar()

# Получение платежей пользователя
async def orm_get_user_payments(session: AsyncSession, user_id: UUID):
    """
    Получение всех платежей пользователя
    """
    query = select(Payment).where(Payment.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

# Получение платежей по событию
async def orm_get_event_payments(session: AsyncSession, event_id: int):
    """
    Получение всех платежей по событию
    """
    query = select(Payment).where(Payment.event_id == event_id)
    result = await session.execute(query)
    return result.scalars().all()

# Получение платежа по регистрации
async def orm_get_payment_by_registration(session: AsyncSession, registration_id: int):
    """
    Получение платежа по ID регистрации
    """
    query = select(Payment).where(Payment.registration_id == registration_id)
    result = await session.execute(query)
    return result.scalar()

# Обновление статуса платежа
async def orm_update_payment_status(
    session: AsyncSession, 
    payment_id: int, 
    status: str
):
    """
    Обновление статуса платежа
    Статусы: pending, completed, failed, refunded, cancelled
    """
    query = update(Payment).where(Payment.id == payment_id).values(
        status=status
    )
    await session.execute(query)
    await session.commit()

# Обновление платежа по payment_id (внешнему ID)
async def orm_update_payment_by_payment_id(
    session: AsyncSession, 
    payment_id: int, 
    data: dict
):
    """
    Обновление платежа по payment_id (внешнему ID платежной системы)
    """
    query = update(Payment).where(Payment.payment_id == payment_id).values(**data)
    await session.execute(query)
    await session.commit()

# Удаление платежа
async def orm_delete_payment(session: AsyncSession, payment_id: int):
    """
    Удаление платежа
    """
    query = delete(Payment).where(Payment.id == payment_id)
    await session.execute(query)
    await session.commit()

# Проверка существования платежа
async def orm_check_payment(session: AsyncSession, payment_id: int):
    """
    Проверка существования платежа по ID
    """
    query = select(Payment).where(Payment.id == payment_id)
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Проверка оплаты регистрации
async def orm_check_registration_payment(session: AsyncSession, registration_id: int):
    """
    Проверка, оплачена ли регистрация
    """
    query = select(Payment).where(
        and_(
            Payment.registration_id == registration_id,
            Payment.status == "completed"
        )
    )
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Получение общей суммы платежей пользователя
async def orm_get_user_total_payments(session: AsyncSession, user_id: UUID):
    """
    Получение общей суммы всех успешных платежей пользователя
    """
    query = select(func.sum(Payment.amount)).where(
        and_(
            Payment.user_id == user_id,
            Payment.status == "completed"
        )
    )
    result = await session.execute(query)
    total = result.scalar()
    return float(total) if total else 0.0

# Получение статистики по платежам события
async def orm_get_event_payment_stats(session: AsyncSession, event_id: int):
    """
    Получение статистики платежей по событию
    """
    # Общая сумма успешных платежей
    total_query = select(func.sum(Payment.amount)).where(
        and_(
            Payment.event_id == event_id,
            Payment.status == "completed"
        )
    )
    total = await session.execute(total_query)
    
    # Количество успешных платежей
    count_query = select(func.count()).where(
        and_(
            Payment.event_id == event_id,
            Payment.status == "completed"
        )
    )
    count = await session.execute(count_query)
    
    # Количество платежей по статусам
    pending_query = select(func.count()).where(
        and_(
            Payment.event_id == event_id,
            Payment.status == "pending"
        )
    )
    pending = await session.execute(pending_query)
    
    failed_query = select(func.count()).where(
        and_(
            Payment.event_id == event_id,
            Payment.status == "failed"
        )
    )
    failed = await session.execute(failed_query)
    
    refunded_query = select(func.count()).where(
        and_(
            Payment.event_id == event_id,
            Payment.status == "refunded"
        )
    )
    refunded = await session.execute(refunded_query)
    
    return {
        "total_amount": float(total.scalar()) if total.scalar() else 0.0,
        "completed_count": count.scalar() or 0,
        "pending_count": pending.scalar() or 0,
        "failed_count": failed.scalar() or 0,
        "refunded_count": refunded.scalar() or 0
    }

# Получение платежей с деталями
async def orm_get_payments_with_details(session: AsyncSession, limit: int = 100):
    """
    Получение последних платежей с деталями пользователей и событий
    """
    query = select(Payment, User, Event).join(
        User, Payment.user_id == User.id
    ).join(
        Event, Payment.event_id == Event.id
    ).order_by(Payment.id.desc()).limit(limit)
    
    result = await session.execute(query)
    payments_with_details = []
    
    for payment, user, event in result:
        payments_with_details.append({
            "payment": payment,
            "user": user,
            "event": event
        })
    
    return payments_with_details

# Получение платежей пользователя с деталями событий
async def orm_get_user_payments_with_events(session: AsyncSession, user_id: UUID):
    """
    Получение всех платежей пользователя с информацией о событиях
    """
    query = select(Payment, Event).join(
        Event, Payment.event_id == Event.id
    ).where(Payment.user_id == user_id).order_by(Payment.id.desc())
    
    result = await session.execute(query)
    payments_with_events = []
    
    for payment, event in result:
        payments_with_events.append({
            "payment": payment,
            "event": event
        })
    
    return payments_with_events
