from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_router.schemas import Response, UserResponse, UserBase
from app.database.engine import get_async_session
from app.database.queries import (
    orm_get_users
)
from app.database.queries.user import orm_add_user, orm_delete_user, orm_get_user


user_router = APIRouter()


@user_router.get('/users', response_model=list[UserResponse])
async def get_users(
    page: int = Query(ge=0, default=0),
    size: int = Query(ge=0, le=100, default=0),
    session: AsyncSession = Depends(get_async_session)
):
    users = await orm_get_users(session, page, size)

    return users


@user_router.post('/users', response_model=Response)
async def add_user(
    user_data: UserBase,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        await orm_add_user(
            session,
            telegram_id=user_data.telegram_id,
            phone=user_data.phone,
            email=user_data.email,
            full_name=user_data.full_name,
            username=user_data.username,
            is_blacklist=user_data.is_blacklist
        )

        return Response(status='success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Eternal server error: {e}')


@user_router.get('/users/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    user = await orm_get_user(session, user_id)

    return user


@user_router.delete('/users/{user_id}')
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    await orm_delete_user(session, user_id)

    return Response(
        status='success',
    )


@user_router.put('/users/{user_id}')
async def update_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    pass

