import os
import logging
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
APP_URL = os.environ["APP_URL"].rstrip("/")  # https://godzi-game.onrender.com

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

PORT = int(os.getenv("PORT", "10000"))
ROOT = Path(__file__).resolve().parent

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🎮 Открыть Godzi Game",
                web_app=WebAppInfo(url=f"{APP_URL}/"),
            )
        ]]
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-приложение 👇", reply_markup=kb)


async def webhook_handler(request: web.Request) -> web.Response:
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")


async def index(request: web.Request) -> web.Response:
    return web.FileResponse(ROOT / "index.html")


def create_app() -> web.Application:
    app = web.Application()

    # Telegram webhook endpoint
    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    # Game index
    app.router.add_get("/", index)

    # Static files from repo root: /images, /music.mp3, etc.
    app.router.add_static("/", path=str(ROOT), show_index=False)

    async def on_startup(app: web.Application):
        webhook_url = f"{APP_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info("Webhook set: %s", webhook_url)

    async def on_shutdown(app: web.Application):
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.session.close()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=PORT)
