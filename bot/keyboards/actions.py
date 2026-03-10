"""Кнопки действий для работы с результатом."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_result_actions_keyboard() -> InlineKeyboardMarkup:
    """Кнопки под результатом: копировать, уточнить, заново."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Уточнить промт", callback_data="action:refine"),
            InlineKeyboardButton(text="🔄 Начать заново", callback_data="action:restart"),
        ],
        [
            InlineKeyboardButton(text="⭐ Оценить (5/5)", callback_data="action:rate:5"),
        ],
    ])


def build_refine_keyboard() -> InlineKeyboardMarkup:
    """Кнопки для режима уточнения."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Изменить роль", callback_data="refine:role"),
            InlineKeyboardButton(text="🎯 Изменить задачу", callback_data="refine:task"),
        ],
        [
            InlineKeyboardButton(text="📐 Изменить контекст", callback_data="refine:context"),
            InlineKeyboardButton(text="⚙️ Изменить формат", callback_data="refine:format"),
        ],
        [
            InlineKeyboardButton(text="✅ Всё отлично!", callback_data="refine:done"),
            InlineKeyboardButton(text="⬅️ Назад", callback_data="action:back_to_result"),
        ],
    ])
