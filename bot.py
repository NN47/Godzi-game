import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://godzi-game.onrender.com")
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    bot = Bot(token=BOT_TOKEN)
    logger.info("Starting bot with WEBAPP_URL=%s", WEBAPP_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
