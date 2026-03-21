import asyncio
import os
import logging
import time
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MenuButtonWebApp,
)
from aiogram.types.web_app_info import WebAppInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
APP_URL = os.environ["APP_URL"].rstrip("/")  # https://godzi-game.onrender.com
APP_VERSION = os.getenv("APP_VERSION") or os.getenv("RENDER_GIT_COMMIT") or str(int(time.time()))

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
                web_app=WebAppInfo(url=f"{APP_URL}/?v={APP_VERSION}"),
            )
        ]]
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-приложение 👇", reply_markup=kb)


async def index(request: web.Request) -> web.Response:
    response = web.FileResponse(ROOT / "index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


def create_app() -> web.Application:
    app = web.Application()

    # Healthcheck / home
    app.router.add_get("/", index)

    # Static files from repo root: /images, /music.mp3, etc.
    app.router.add_static("/", path=str(ROOT), show_index=False)

    return app


async def run_web_server() -> None:
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info("Web server started on port %s", PORT)


async def main() -> None:
    # Switch bot updates to polling mode.
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook removed, starting polling")
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🎮 Godzi Game",
            web_app=WebAppInfo(url=f"{APP_URL}/?v={APP_VERSION}"),
        )
    )
    logger.info("Menu button updated with app version %s", APP_VERSION)

    await run_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
