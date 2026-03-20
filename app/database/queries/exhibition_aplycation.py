from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import ExhibitionApplications, User

# Добавление заявки
async def orm_add_exhibition_application(
    session: AsyncSession,
    user_id: int,
    legal_status: str,
    company_name: str,
    contact_person: str,
    activity_description: str,
    provided_type: str,
    need_support: bool = False,
    full_price: Optional[float] = None,
    support_amount: Optional[float] = None,
    full_amount: Optional[float] = None,
    payment_status: str = "unpaid",
    status: str = "new"
):
    """
    Добавление новой заявки на выставку
    """
    session.add(ExhibitionApplications(
        user_id=user_id,
        legal_status=legal_status,
        company_name=company_name,
        contact_person=contact_person,
        activity_description=activity_description,
        provided_type=provided_type,
        need_support=need_support,
        full_price=full_price,
        support_amount=support_amount,
        full_amount=full_amount,
        payment_status=payment_status,
        status=status
    ))
    await session.commit()

# Получение всех заявок
async def orm_get_exhibition_applications(session: AsyncSession):
    """
    Получение всех заявок
    """
    query = select(ExhibitionApplications)
    result = await session.execute(query)
    return result.scalars().all()

# Получение одной заявки по ID
async def orm_get_exhibition_application(session: AsyncSession, application_id: int):
    """
    Получение заявки по ID
    """
    query = select(ExhibitionApplications).where(ExhibitionApplications.id == application_id)
    result = await session.execute(query)
    return result.scalar()

# Получение заявок пользователя
async def orm_get_user_exhibition_applications(session: AsyncSession, user_id: int):
    """
    Получение всех заявок пользователя
    """
    query = select(ExhibitionApplications).where(ExhibitionApplications.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

# Получение заявок по статусу
async def orm_get_applications_by_status(session: AsyncSession, status: str):
    """
    Получение заявок с определенным статусом
    """
    query = select(ExhibitionApplications).where(ExhibitionApplications.status == status)
    result = await session.execute(query)
    return result.scalars().all()

# Обновление заявки
async def orm_update_exhibition_application(
    session: AsyncSession,
    application_id: int,
    data: dict
):
    """
    Обновление данных заявки
    """
    query = update(ExhibitionApplications).where(
        ExhibitionApplications.id == application_id
    ).values(**data)
    await session.execute(query)
    await session.commit()

# Изменение статуса заявки
async def orm_change_application_status(
    session: AsyncSession,
    application_id: int,
    status: str
):
    """
    Изменение статуса заявки
    """
    query = update(ExhibitionApplications).where(
        ExhibitionApplications.id == application_id
    ).values(status=status)
    await session.execute(query)
    await session.commit()

# Изменение статуса оплаты
async def orm_change_payment_status(
    session: AsyncSession,
    application_id: int,
    payment_status: str
):
    """
    Изменение статуса оплаты
    """
    query = update(ExhibitionApplications).where(
        ExhibitionApplications.id == application_id
    ).values(payment_status=payment_status)
    await session.execute(query)
    await session.commit()

# Удаление заявки
async def orm_delete_exhibition_application(session: AsyncSession, application_id: int):
    """
    Удаление заявки
    """
    query = delete(ExhibitionApplications).where(ExhibitionApplications.id == application_id)
    await session.execute(query)
    await session.commit()

# Проверка существования заявки
async def orm_check_exhibition_application(session: AsyncSession, application_id: int):
    """
    Проверка существования заявки
    """
    query = select(ExhibitionApplications).where(ExhibitionApplications.id == application_id)
    result = await session.execute(query)
    return result.first() is not None

# Получение заявок с данными пользователей
async def orm_get_applications_with_users(session: AsyncSession):
    """
    Получение всех заявок с информацией о пользователях
    """
    query = select(ExhibitionApplications, User).join(
        User, ExhibitionApplications.user_id == User.id
    )
    result = await session.execute(query)
    
    applications = []
    for app, user in result:
        applications.append({
            "application": app,
            "user": user
        })
    return applications



