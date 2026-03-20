from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api_router.api import api_router
from app.admin_panel_router.admin_panel import admin_router
from app.tg_bot_router.bot import dp, bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    url_webhook = ""
    await bot.set_webhook(url=url_webhook,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    yield
    await bot.delete_webhook()


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/admin_panel_router/static"), name="static")

app.include_router(api_router)
app.include_router(admin_router, tags=['Dashboard'])



