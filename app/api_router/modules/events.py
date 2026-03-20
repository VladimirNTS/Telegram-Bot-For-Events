from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_router.schemas import EventBase, EventResponse, Response
from app.database.engine import get_async_session
from app.database.queries.events import orm_add_event, orm_delete_event, orm_get_event, orm_get_events


event_router = APIRouter(prefix='/events')


@event_router.get('', response_model=list[EventResponse])
async def get_users(
    page: int = Query(ge=0, default=0),
    size: int = Query(ge=0, le=100, default=0),
    session: AsyncSession = Depends(get_async_session)
):
    users = await orm_get_events(session, page, size)

    return users


@event_router.post('')
async def add_user(
    event_data: EventBase,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # `Event.timezone` хранит таймзону отдельно, поэтому `start_datetime` лучше держать без tzinfo.
        start_dt = event_data.start_datetime
        if getattr(start_dt, "tzinfo", None) is not None:
            start_dt = start_dt.replace(tzinfo=None)

        await orm_add_event(
            session,
            title=event_data.title,
            section=event_data.section,
            description=event_data.description,
            location=event_data.location,
            max_participants=event_data.max_participants,
            start_datetime=start_dt,
            participation_conditions=event_data.participation_conditions,
            price=event_data.price,
            status=event_data.status,
            timezone=event_data.timezone
        )

        return Response(status='success')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Eternal server error: {e}')


@event_router.get('/{event_id}', response_model=EventResponse)
async def get_user(
    event_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    user = await orm_get_event(session, event_id)

    return user


@event_router.delete('/{event_id}')
async def delete_user(
    event_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    await orm_delete_event(session, event_id)

    return Response(
        status='success',
    )


@event_router.put('/{event_id}')
async def update_user(
    event_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    pass

