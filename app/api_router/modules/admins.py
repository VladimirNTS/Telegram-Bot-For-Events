# api/admin/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.engine import get_async_session
from app.utils.admin_permision import require_any_admin
from app.utils.security import create_access_token
from app.database.queries import orm_authenticate_admin, orm_get_admin_by_login
from app.config import settings

admin_router = APIRouter(prefix="/auth")

@admin_router.post("/login")
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """Логин администратора"""
    admin = await orm_authenticate_admin(
        session, 
        form_data.username, 
        form_data.password
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Собираем права доступа
    permissions = {
        "events": admin.events,
        "registers": admin.registers,
        "partners_apply": admin.partners_apply,
        "exhibitions_apply": admin.exhibitions_apply,
        "users": admin.users,
        "queue": admin.queue,
        "payments": admin.payments,
        "documents": admin.documents,
        "reviews": admin.reviews,
        "notifications": admin.notifications,
        "support": admin.support,
        "qr_codes": admin.qr_codes
    }
    
    # Создаем JWT токен с правами
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": admin.login,
            "type": "admin",
            "super_user": admin.super_user,
            "permissions": permissions
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "super_user": admin.super_user,
        "permissions": permissions,
        "login": admin.login
    }

@admin_router.get("/me")
async def get_current_admin_info(
    admin_data = Depends(require_any_admin()),
    session: AsyncSession = Depends(get_async_session)
):
    """Получить информацию о текущем администраторе"""
    admin = await orm_get_admin_by_login(session, admin_data.login)
    if not admin:
        return HTTPException(status_code=403)
    return {
        "login": admin.login,
        "super_user": admin.super_user,
        "permissions": {
            "events": admin.events,
            "registers": admin.registers,
            "partners_apply": admin.partners_apply,
            "exhibitions_apply": admin.exhibitions_apply,
            "users": admin.users,
            "queue": admin.queue,
            "payments": admin.payments,
            "documents": admin.documents,
            "reviews": admin.reviews,
            "notifications": admin.notifications,
            "support": admin.support,
            "qr_codes": admin.qr_codes
        }
    }
