from typing import Optional
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from app.database.models import PartnerApplication, User  # импортируйте ваши модели

# Константы для статусов заявок
PARTNER_STATUS = {
    "NEW": "new",  # Новая заявка
    "PENDING": "pending",  # На рассмотрении
    "APPROVED": "approved",  # Одобрена
    "REJECTED": "rejected",  # Отклонена
    "IN_PROGRESS": "in_progress",  # В процессе переговоров
    "COMPLETED": "completed",  # Завершена (стали партнерами)
    "ARCHIVED": "archived"  # В архиве
}

# Добавление заявки партнера
async def orm_add_partner_application(
    session: AsyncSession,
    user_id: UUID,
    direction: str,
    cooperation_format: str,
    benefit_description: str,
    comment: Optional[str] = None,
    status: str = PARTNER_STATUS["NEW"],
    admin_notes: str = ""
):
    """
    Добавление новой заявки партнера
    """
    session.add(PartnerApplication(
        user_id=user_id,
        direction=direction,
        cooperation_format=cooperation_format,
        benefit_description=benefit_description,
        comment=comment,
        status=status,
        admin_notes=admin_notes
    ))
    await session.commit()

# Получение всех заявок
async def orm_get_partner_applications(session: AsyncSession):
    """
    Получение всех заявок партнеров
    """
    query = select(PartnerApplication)
    result = await session.execute(query)
    return result.scalars().all()

# Получение одной заявки по ID
async def orm_get_partner_application(session: AsyncSession, application_id: int):
    """
    Получение заявки партнера по её ID
    """
    query = select(PartnerApplication).where(PartnerApplication.id == application_id)
    result = await session.execute(query)
    return result.scalar()

# Получение заявок пользователя
async def orm_get_user_partner_applications(session: AsyncSession, user_id: UUID):
    """
    Получение всех заявок конкретного пользователя
    """
    query = select(PartnerApplication).where(
        PartnerApplication.user_id == user_id
    ).order_by(PartnerApplication.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

# Получение активных заявок пользователя
async def orm_get_user_active_applications(session: AsyncSession, user_id: UUID):
    """
    Получение активных заявок пользователя (не отклоненных и не в архиве)
    """
    query = select(PartnerApplication).where(
        and_(
            PartnerApplication.user_id == user_id,
            PartnerApplication.status.in_([
                PARTNER_STATUS["NEW"],
                PARTNER_STATUS["PENDING"],
                PARTNER_STATUS["IN_PROGRESS"]
            ])
        )
    )
    result = await session.execute(query)
    return result.scalars().all()

# Получение заявок по статусу
async def orm_get_applications_by_status(session: AsyncSession, status: str):
    """
    Получение заявок с определенным статусом
    """
    query = select(PartnerApplication).where(
        PartnerApplication.status == status
    ).order_by(PartnerApplication.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

# Получение заявок по направлению
async def orm_get_applications_by_direction(session: AsyncSession, direction: str):
    """
    Получение заявок по направлению партнерства
    """
    query = select(PartnerApplication).where(
        PartnerApplication.direction == direction
    ).order_by(PartnerApplication.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

# Получение заявок по формату сотрудничества
async def orm_get_applications_by_format(session: AsyncSession, cooperation_format: str):
    """
    Получение заявок по формату сотрудничества
    """
    query = select(PartnerApplication).where(
        PartnerApplication.cooperation_format == cooperation_format
    ).order_by(PartnerApplication.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

# Обновление заявки
async def orm_update_partner_application(
    session: AsyncSession,
    application_id: int,
    data: dict
):
    """
    Обновление информации о заявке
    data может содержать: direction, cooperation_format, benefit_description, 
    comment, status, admin_notes
    """
    query = update(PartnerApplication).where(
        PartnerApplication.id == application_id
    ).values(**data)
    await session.execute(query)
    await session.commit()

# Изменение статуса заявки
async def orm_change_application_status(
    session: AsyncSession,
    application_id: int,
    status: str,
    admin_notes: Optional[str] = None
):
    """
    Изменение статуса заявки с возможностью добавить заметки администратора
    """
    values = {"status": status}
    if admin_notes is not None:
        values["admin_notes"] = admin_notes
    
    query = update(PartnerApplication).where(
        PartnerApplication.id == application_id
    ).values(**values)
    await session.execute(query)
    await session.commit()

# Добавление заметки администратора
async def orm_add_admin_notes(
    session: AsyncSession,
    application_id: int,
    admin_notes: str
):
    """
    Добавление или обновление заметок администратора
    """
    query = update(PartnerApplication).where(
        PartnerApplication.id == application_id
    ).values(admin_notes=admin_notes)
    await session.execute(query)
    await session.commit()

# Одобрение заявки
async def orm_approve_application(
    session: AsyncSession,
    application_id: int,
    admin_notes: Optional[str] = None
):
    """
    Одобрение заявки партнера
    """
    await orm_change_application_status(
        session,
        application_id,
        PARTNER_STATUS["APPROVED"],
        admin_notes
    )

# Отклонение заявки
async def orm_reject_application(
    session: AsyncSession,
    application_id: int,
    admin_notes: Optional[str] = None
):
    """
    Отклонение заявки партнера с указанием причины
    """
    await orm_change_application_status(
        session,
        application_id,
        PARTNER_STATUS["REJECTED"],
        admin_notes
    )

# Удаление заявки
async def orm_delete_partner_application(session: AsyncSession, application_id: int):
    """
    Удаление заявки партнера
    """
    query = delete(PartnerApplication).where(PartnerApplication.id == application_id)
    await session.execute(query)
    await session.commit()

# Проверка существования заявки
async def orm_check_partner_application(session: AsyncSession, application_id: int):
    """
    Проверка существования заявки по ID
    """
    query = select(PartnerApplication).where(PartnerApplication.id == application_id)
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Проверка наличия активной заявки у пользователя
async def orm_check_user_has_active_application(
    session: AsyncSession,
    user_id: UUID
):
    """
    Проверка, есть ли у пользователя активная заявка
    """
    query = select(PartnerApplication).where(
        and_(
            PartnerApplication.user_id == user_id,
            PartnerApplication.status.in_([
                PARTNER_STATUS["NEW"],
                PARTNER_STATUS["PENDING"],
                PARTNER_STATUS["IN_PROGRESS"]
            ])
        )
    )
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Получение последней заявки пользователя
async def orm_get_user_latest_application(session: AsyncSession, user_id: UUID):
    """
    Получение последней заявки пользователя
    """
    query = select(PartnerApplication).where(
        PartnerApplication.user_id == user_id
    ).order_by(PartnerApplication.id.desc()).limit(1)
    result = await session.execute(query)
    return result.scalar()

# Получение статистики по заявкам
async def orm_get_partner_applications_stats(session: AsyncSession):
    """
    Получение статистики по всем заявкам
    """
    # Общее количество
    total_query = select(func.count()).select_from(PartnerApplication)
    total = await session.execute(total_query)
    
    # По статусам
    new_query = select(func.count()).where(
        PartnerApplication.status == PARTNER_STATUS["NEW"]
    )
    new = await session.execute(new_query)
    
    pending_query = select(func.count()).where(
        PartnerApplication.status == PARTNER_STATUS["PENDING"]
    )
    pending = await session.execute(pending_query)
    
    approved_query = select(func.count()).where(
        PartnerApplication.status == PARTNER_STATUS["APPROVED"]
    )
    approved = await session.execute(approved_query)
    
    rejected_query = select(func.count()).where(
        PartnerApplication.status == PARTNER_STATUS["REJECTED"]
    )
    rejected = await session.execute(rejected_query)
    
    in_progress_query = select(func.count()).where(
        PartnerApplication.status == PARTNER_STATUS["IN_PROGRESS"]
    )
    in_progress = await session.execute(in_progress_query)
    
    # По направлениям
    directions_query = select(
        PartnerApplication.direction,
        func.count().label('count')
    ).group_by(PartnerApplication.direction)
    directions = await session.execute(directions_query)
    
    # По форматам сотрудничества
    formats_query = select(
        PartnerApplication.cooperation_format,
        func.count().label('count')
    ).group_by(PartnerApplication.cooperation_format)
    formats = await session.execute(formats_query)
    
    return {
        "total": total.scalar() or 0,
        "by_status": {
            "new": new.scalar() or 0,
            "pending": pending.scalar() or 0,
            "approved": approved.scalar() or 0,
            "rejected": rejected.scalar() or 0,
            "in_progress": in_progress.scalar() or 0
        },
        "by_direction": {dir: count for dir, count in directions},
        "by_format": {fmt: count for fmt, count in formats}
    }

# Получение заявок с деталями пользователей
async def orm_get_applications_with_users(
    session: AsyncSession,
    status: Optional[str] = None,
    limit: int = 100
):
    """
    Получение заявок с информацией о пользователях
    """
    query = select(PartnerApplication, User).join(
        User, PartnerApplication.user_id == User.id
    )
    
    if status:
        query = query.where(PartnerApplication.status == status)
    
    query = query.order_by(PartnerApplication.id.desc()).limit(limit)
    
    result = await session.execute(query)
    applications_with_users = []
    
    for application, user in result:
        applications_with_users.append({
            "application": application,
            "user": user
        })
    
    return applications_with_users

# Поиск заявок по тексту
async def orm_search_applications(
    session: AsyncSession,
    search_term: str
):
    """
    Поиск заявок по описанию выгоды или комментарию
    """
    query = select(PartnerApplication).where(
        or_(
            PartnerApplication.benefit_description.ilike(f"%{search_term}%"),
            PartnerApplication.comment.ilike(f"%{search_term}%"),
            PartnerApplication.admin_notes.ilike(f"%{search_term}%")
        )
    ).order_by(PartnerApplication.id.desc())
    
    result = await session.execute(query)
    return result.scalars().all()
