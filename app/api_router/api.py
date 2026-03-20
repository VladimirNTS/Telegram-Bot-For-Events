from fastapi import APIRouter

from app.api_router.modules import user_router, event_router, admin_router


api_router = APIRouter(prefix='/api')
api_router.include_router(admin_router, tags=['Admin'])
api_router.include_router(user_router, tags=['User'])
api_router.include_router(event_router, tags=['Events'])


