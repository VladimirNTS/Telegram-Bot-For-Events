from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from datetime import datetime
from app.database.models import User  # импортируйте ваш модель

# Добавление пользователя
async def orm_add_user(
    session: AsyncSession,
    telegram_id: str,
    username: str,
    full_name: str,
    phone: str,
    email: str,
    is_blacklist: bool = False,
):
    """
    Добавление нового пользователя
    """
    session.add(User(
        id=uuid4(),
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        phone=phone,
        email=email,
        status=0,
        section_id=1,
        last_event=None,
        is_blacklist=is_blacklist
    ))
    await session.commit()

# Получение всех пользователей
async def orm_get_users(
    session: AsyncSession,
    page: Optional[int] = None,
    size: Optional[int] = None,
):
    """
    Получение всех пользователей
    """
    query = select(User)
    result = await session.execute(query)
    if size:
        min_offset = size * page
        max_offset = size * page + 1 
        return result.scalars().all()[min_offset:max_offset]
    else:
        return result.scalars().all()


# Получение одного пользователя по ID
async def orm_get_user(session: AsyncSession, user_id: UUID):
    """
    Получение пользователя по его UUID
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()

# Получение пользователя по telegram_id
async def orm_get_user_by_telegram_id(session: AsyncSession, telegram_id: str):
    """
    Получение пользователя по telegram_id
    """
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()

# Обновление данных пользователя
async def orm_update_user(session: AsyncSession, user_id: UUID, data: dict):
    """
    Обновление информации о пользователе
    data может содержать: username, full_name, phone, email, status, section_id, is_blacklist
    """
    query = update(User).where(User.id == user_id).values(**data)
    await session.execute(query)
    await session.commit()

# Обновление времени последнего события
async def orm_update_last_event(session: AsyncSession, user_id: UUID):
    """
    Обновление времени последнего события пользователя
    """
    query = update(User).where(User.id == user_id).values(
        last_event=datetime.now()
    )
    await session.execute(query)
    await session.commit()

# Добавление в черный список
async def orm_blacklist_user(session: AsyncSession, user_id: UUID, blacklist: bool = True):
    """
    Добавление или удаление пользователя из черного списка
    """
    query = update(User).where(User.id == user_id).values(
        is_blacklist=blacklist
    )
    await session.execute(query)
    await session.commit()

# Изменение секции пользователя
async def orm_change_section(session: AsyncSession, user_id: UUID, section_id: int):
    """
    Изменение секции пользователя
    """
    query = update(User).where(User.id == user_id).values(
        section_id=section_id
    )
    await session.execute(query)
    await session.commit()

# Изменение статуса пользователя
async def orm_change_status(session: AsyncSession, user_id: UUID, status: int):
    """
    Изменение статуса пользователя
    """
    query = update(User).where(User.id == user_id).values(
        status=status
    )
    await session.execute(query)
    await session.commit()

# Удаление пользователя
async def orm_delete_user(session: AsyncSession, user_id: UUID):
    """
    Удаление пользователя
    """
    query = delete(User).where(User.id == user_id)
    await session.execute(query)
    await session.commit()

# Проверка наличия пользователя в базе
async def orm_check_user(session: AsyncSession, telegram_id: str):
    """
    Проверка существования пользователя по telegram_id
    """
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Проверка наличия пользователя в черном списке
async def orm_check_blacklist(session: AsyncSession, telegram_id: str):
    """
    Проверка, находится ли пользователь в черном списке
    """
    query = select(User).where(
        User.telegram_id == telegram_id,
        User.is_blacklist == True
    )
    result = await session.execute(query)
    if result.first() is None:
        return False
    return True

# Получение всех пользователей из определенной секции
async def orm_get_users_by_section(session: AsyncSession, section_id: int):
    """
    Получение всех пользователей из указанной секции
    """
    query = select(User).where(User.section_id == section_id)
    result = await session.execute(query)
    return result.scalars().all()

# Получение всех пользователей с определенным статусом
async def orm_get_users_by_status(session: AsyncSession, status: int):
    """
    Получение всех пользователей с указанным статусом
    """
    query = select(User).where(User.status == status)
    result = await session.execute(query)
    return result.scalars().all()

# Получение пользователей из черного списка
async def orm_get_blacklisted_users(session: AsyncSession):
    """
    Получение всех пользователей из черного списка
    """
    query = select(User).where(User.is_blacklist == True)
    result = await session.execute(query)
    return result.scalars().all()


