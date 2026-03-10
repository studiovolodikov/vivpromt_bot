"""Handler: Обработка выбора категорий, подкатегорий и типов задач."""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.categories import (
    CATEGORIES,
    TASK_TYPE_LABELS,
    build_categories_keyboard,
    build_subcategories_keyboard,
    build_task_types_keyboard,
)
from bot.states.interview import InterviewStates

router = Router(name="category")


# ═══════════════════════════════════════════════════════════
#  Выбор категории (уровень 1)
# ═══════════════════════════════════════════════════════════


@router.callback_query(InterviewStates.choosing_category, F.data.startswith("cat:"))
async def on_category_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь выбрал категорию → показываем подкатегории."""
    category_key = callback.data.split(":")[1]
    category = CATEGORIES.get(category_key)

    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    await state.update_data(category=category_key, category_label=category["label"])
    await state.set_state(InterviewStates.choosing_subcategory)

    keyboard = build_subcategories_keyboard(category_key)
    await callback.message.edit_text(
        text=f"{category['label']}\n\nВыберите направление:",
        reply_markup=keyboard,
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
#  Выбор подкатегории (уровень 2)
# ═══════════════════════════════════════════════════════════


@router.callback_query(InterviewStates.choosing_subcategory, F.data.startswith("sub:"))
async def on_subcategory_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь выбрал подкатегорию → показываем типы задач."""
    parts = callback.data.split(":")
    category_key, subcategory_key = parts[1], parts[2]

    category = CATEGORIES.get(category_key, {})
    subcategory = category.get("subcategories", {}).get(subcategory_key, {})

    if not subcategory:
        await callback.answer("Подкатегория не найдена", show_alert=True)
        return

    await state.update_data(
        subcategory=subcategory_key,
        subcategory_label=subcategory["label"],
    )
    await state.set_state(InterviewStates.choosing_task_type)

    keyboard = build_task_types_keyboard(category_key, subcategory_key)
    await callback.message.edit_text(
        text=f"{subcategory['label']}\n\nЧто нужно сделать?",
        reply_markup=keyboard,
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
#  Выбор типа задачи (уровень 3) → Переход к AI-интервью
# ═══════════════════════════════════════════════════════════


@router.callback_query(InterviewStates.choosing_task_type, F.data.startswith("task:"))
async def on_task_type_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь выбрал тип задачи → запускаем AI-интервью."""
    parts = callback.data.split(":")
    task_type = parts[3]
    task_label = TASK_TYPE_LABELS.get(task_type, task_type)

    await state.update_data(task_type=task_type, task_label=task_label)
    await state.set_state(InterviewStates.ai_interview)

    # Запрашиваем первый вопрос от AI
    data = await state.get_data()
    summary = (
        f"Сфера: {data.get('category_label', '')}, "
        f"Направление: {data.get('subcategory_label', '')}, "
        f"Действие: {task_label}"
    )

    await callback.message.edit_text(
        text=(
            f"✅ Отлично\\!\n\n"
            f"📂 {data.get('category_label', '')}"
            f" → {data.get('subcategory_label', '')}"
            f" → {task_label}\n\n"
            f"🧠 Теперь я задам несколько уточняющих вопросов, "
            f"чтобы создать идеальный промт\\.\n\n"
            f"*Опишите вашу задачу подробнее:*"
        ),
        parse_mode="MarkdownV2",
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
#  Навигация: кнопка «Назад»
# ═══════════════════════════════════════════════════════════


@router.callback_query(F.data == "back:categories")
async def on_back_to_categories(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат к списку категорий."""
    await state.set_state(InterviewStates.choosing_category)
    await callback.message.edit_text(
        text="🎯 Выберите сферу деятельности:",
        reply_markup=build_categories_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back:sub:"))
async def on_back_to_subcategories(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат к списку подкатегорий."""
    category_key = callback.data.split(":")[2]
    await state.set_state(InterviewStates.choosing_subcategory)

    category = CATEGORIES.get(category_key, {})
    keyboard = build_subcategories_keyboard(category_key)
    await callback.message.edit_text(
        text=f"{category.get('label', '')}\n\nВыберите направление:",
        reply_markup=keyboard,
    )
    await callback.answer()
