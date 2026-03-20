from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin_panel_router.dependencies import (
    ADMIN_AUTH_COOKIE_NAME,
    require_any_admin_cookie,
    require_viewer_cookie,
)
from app.config import settings
from app.database.engine import get_async_session
from app.database.queries import orm_authenticate_admin, orm_get_events
from app.utils.security import create_access_token


admin_router = APIRouter(prefix='/admin')
templates = Jinja2Templates(directory="app/admin_panel_router/templates")


@admin_router.get("/")
async def get_dash_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("events")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "index.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/events")
async def get_events_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("events")),
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(0, ge=0, description="Номер страницы (с 0)"),
    size: int = Query(10, ge=1, le=100, description="Количество строк на страницу"),
):
    """Страница мероприятий"""
    from app.database.queries.events import orm_count_events

    events = await orm_get_events(session, page, size)
    total_count = await orm_count_events(session)
    total_pages = (total_count + size - 1) // size if size else 1

    return templates.TemplateResponse(
        "events.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Мероприятия",
            "admin": admin_data,
            "events": events,
            "page": page,
            "size": size,
            "total_count": total_count,
            "total_pages": total_pages,
        }
    )


@admin_router.get("/registrations")
async def get_registrations_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("registers")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "registrations.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/exhibition_applies")
async def get_exhibition_applies_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("exhibitions_apply")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "exhibition_applies.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/partner_applies")
async def get_partner_applies_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("partners_apply")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "partner_applies.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/users")
async def get_users_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("users")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "users.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/queue")
async def get_queue_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("queue")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "queue.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/payments")
async def get_payments_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("payments")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "payments.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/documents")
async def get_documents_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("documents")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "documents.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/feedback")
async def get_feedback_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("reviews")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "feedback.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/noftications")
async def get_noftications_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("notifications")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "noftications.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/communication")
async def get_communication_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("support")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "communication.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/qr")
async def get_qr_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("qr_codes")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "qr.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/black_list")
async def get_black_list_page(
    request: Request,
    admin_data=Depends(require_viewer_cookie("users")),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "black_list.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )


@admin_router.get("/settings")
async def get_settings_page(
    request: Request,
    admin_data=Depends(require_any_admin_cookie),
):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "settings.html",  # Можно создать отдельный шаблон
        {
            "request": request,
            "title": "Пользователи",
            "admin": admin_data,
        }
    )

@admin_router.get("/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(ADMIN_AUTH_COOKIE_NAME)
    return response

@admin_router.get("/login")
async def get_login_page(request: Request):
    """Страница пользователей"""
    return templates.TemplateResponse(
        "login.html",  # Можно создать отдельный шабло
        {
            "request": request,
            "title": "Пользователи"
        }
    )


@admin_router.post("/login")
async def admin_login_web(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    admin = await orm_authenticate_admin(session, username, password)
    if not admin:
        response = RedirectResponse(url="/admin/login", status_code=302)
        return response

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
        "qr_codes": admin.qr_codes,
    }

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={
            "sub": admin.login,
            "type": "admin",
            "super_user": admin.super_user,
            "permissions": permissions,
        },
        expires_delta=access_token_expires,
    )

    response = RedirectResponse(url="/admin/", status_code=302)
    response.set_cookie(
        key=ADMIN_AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


