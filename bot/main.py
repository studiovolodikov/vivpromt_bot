"""Prompt Strategist Bot — Main entry point.

Запуск: python -m bot.main
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.handlers import start, category, interview
from bot.middleware.rate_limit import RateLimitMiddleware


def setup_logging() -> None:
    """Настройка логирования."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Приглушаем шумные библиотеки
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)


async def main() -> None:
    """Инициализация и запуск бота."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting Prompt Strategist Bot...")

    # ── Bot & Dispatcher ──────────────────────────────────
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # ── Middleware ─────────────────────────────────────────
    dp.message.middleware(RateLimitMiddleware())

    # ── Routers ───────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(category.router)
    dp.include_router(interview.router)

    # ── Startup ───────────────────────────────────────────
    logger.info("Bot started ✅")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped 🛑")


if __name__ == "__main__":
    asyncio.run(main())
