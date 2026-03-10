"""Rate-limiting middleware для защиты от спама."""

from __future__ import annotations

import time
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Ограничивает количество запросов от одного пользователя."""

    def __init__(self) -> None:
        self._user_timestamps: dict[int, list[float]] = defaultdict(list)
        self._limit = settings.rate_limit_per_minute
        self._window = 60.0  # секунд

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Проверяем rate limit перед передачей обработчику."""
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else 0
        now = time.monotonic()

        # Очищаем устаревшие записи
        timestamps = self._user_timestamps[user_id]
        self._user_timestamps[user_id] = [
            ts for ts in timestamps if now - ts < self._window
        ]

        if len(self._user_timestamps[user_id]) >= self._limit:
            logger.warning("Rate limit exceeded for user %d", user_id)
            await event.answer(
                f"⚠️ Слишком много запросов. "
                f"Подождите {int(self._window - (now - self._user_timestamps[user_id][0]))} сек."
            )
            return None

        self._user_timestamps[user_id].append(now)
        return await handler(event, data)
