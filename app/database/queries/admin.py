from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.utils.security import get_password_hash, verify_password
from app.database.models import Admin


async def orm_create_admin(
    session: AsyncSession,
    login: str,
    password: str,
    super_user: bool = False,
    **permissions
) -> Admin:
    """Создание администратора"""
    password_hash = get_password_hash(password)
    
    # Права по умолчанию
    default_perms = {
        "events": "forbidden",
        "registers": "forbidden",
        "partners_apply": "forbidden",
        "exhibitions_apply": "forbidden",
        "users": "forbidden",
        "queue": "forbidden",
        "payments": "forbidden",
        "documents": "forbidden",
        "reviews": "forbidden",
        "notifications": "forbidden",
        "support": "forbidden",
        "qr_codes": "forbidden"
    }
    
    # Обновляем переданными правами
    default_perms.update(permissions)
    
    admin = Admin(
        login=login,
        password_hash=password_hash,
        super_user=super_user,
        **default_perms
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


async def orm_get_admin_by_login(
    session: AsyncSession,
    login: str
) -> Admin | None:
    """Получение админа по логину"""
    query = select(Admin).where(Admin.login == login)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_get_admin_by_id(
    session: AsyncSession,
    admin_id: UUID
) -> Admin | None:
    """Получение админа по ID"""
    query = select(Admin).where(Admin.id == admin_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_get_all_admins(
    session: AsyncSession
):
    """Получение всех администраторов"""
    query = select(Admin).order_by(Admin.login)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_update_admin(
    session: AsyncSession,
    admin_id: UUID,
    **kwargs
) -> Admin | None:
    """Обновление администратора"""
    # Если передан пароль - хешируем
    if "password" in kwargs:
        kwargs["password_hash"] = get_password_hash(kwargs.pop("password"))
    
    query = update(Admin).where(Admin.id == admin_id).values(**kwargs)
    await session.execute(query)
    await session.commit()
    

async def orm_delete_admin(
    session: AsyncSession,
    admin_id: UUID
) -> bool:
    """Удаление администратора"""
    query = delete(Admin).where(Admin.id == admin_id)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount > 0


async def orm_authenticate_admin(
    session: AsyncSession,
    login: str,
    password: str
) -> Admin | None:
    """Аутентификация администратора"""
    admin = await orm_get_admin_by_login(session, login)
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin
