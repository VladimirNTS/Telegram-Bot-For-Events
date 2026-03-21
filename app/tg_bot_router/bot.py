import os

from aiogram import Bot, types, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


bot = Bot(token=str(os.getenv('TG_TOKEN')), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

