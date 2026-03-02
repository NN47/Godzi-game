import asyncio
import logging
import os
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

WEBAPP_HOST = os.getenv("WEBAPP_HOST", "127.0.0.1")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
WEBAPP_URL = os.getenv("WEBAPP_URL", f"http://{WEBAPP_HOST}:{WEBAPP_PORT}/index.html")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROJECT_DIR = Path(__file__).resolve().parent

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mini_app_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🎮 Открыть Godzi Game",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ],
        resize_keyboard=True,
    )


def create_static_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", lambda request: web.FileResponse(PROJECT_DIR / "index.html"))
    app.router.add_get("/index.html", lambda request: web.FileResponse(PROJECT_DIR / "index.html"))
    app.router.add_static("/images", path=PROJECT_DIR / "images", show_index=False)
    app.router.add_get("/music.mp3", lambda request: web.FileResponse(PROJECT_DIR / "music.mp3"))
    return app


async def start_web_server() -> web.AppRunner:
    app = create_static_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()
    logger.info("Serving game files at %s", WEBAPP_URL)
    return runner


dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Нажми кнопку ниже, чтобы открыть мини‑приложение Godzi Game.",
        reply_markup=mini_app_keyboard(),
    )


@dp.message(F.text == "🎮 Открыть Godzi Game")
async def open_game_hint(message: Message) -> None:
    await message.answer("Нажми на кнопку внизу, чтобы запустить игру в Telegram Mini App.")


async def main() -> None:
    runner = await start_web_server()
    bot = Bot(token=BOT_TOKEN)
    logger.info("Starting bot with WEBAPP_URL=%s", WEBAPP_URL)
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
