"""Handler: /start — Приветствие и инициализация сессии."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards.categories import build_categories_keyboard
from bot.states.interview import InterviewStates

router = Router(name="start")

WELCOME_TEXT = (
    "🎯 *Prompt Strategist Bot*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Я помогу вам создать *профессиональный промт* "
    "и подберу лучшие *Skills* и *MCP\\-серверы* "
    "для решения вашей задачи\\.\n\n"
    "Выберите сферу деятельности:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start."""
    # Сбрасываем состояние на случай перезапуска
    await state.clear()
    await state.set_state(InterviewStates.choosing_category)

    await message.answer(
        text=WELCOME_TEXT,
        reply_markup=build_categories_keyboard(),
        parse_mode="MarkdownV2",
    )
