"""Handler: AI-интервью — уточняющие вопросы и генерация промта."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.actions import build_refine_keyboard, build_result_actions_keyboard
from bot.states.interview import InterviewStates
from bot.utils.formatting import format_prompt_result, format_recommendations
from core.ai_engine import AIEngine, InterviewContext
from core.recommender import Recommender

logger = logging.getLogger(__name__)

router = Router(name="interview")

# Синглтоны (инициализируются один раз)
_ai_engine = AIEngine()
_recommender = Recommender()


# ═══════════════════════════════════════════════════════════
#  AI-интервью: приём свободных текстовых ответов
# ═══════════════════════════════════════════════════════════


@router.message(InterviewStates.ai_interview)
async def on_interview_answer(message: Message, state: FSMContext) -> None:
    """Пользователь отвечает на вопрос AI → проверяем, нужно ли ещё."""
    data = await state.get_data()
    user_text = message.text or ""

    # Восстанавливаем контекст
    ctx = InterviewContext(
        category=data.get("category_label", ""),
        subcategory=data.get("subcategory_label", ""),
        task_type=data.get("task_label", ""),
        answers=data.get("interview_answers", []),
        question_count=data.get("question_count", 0),
    )

    # Сохраняем текущий ответ
    last_question = data.get("last_question", "Опишите задачу")
    ctx.answers.append({"question": last_question, "answer": user_text})
    ctx.question_count += 1

    # Отправляем индикатор набора текста
    await message.bot.send_chat_action(message.chat.id, "typing")

    # Спрашиваем AI: нужен ли ещё вопрос?
    try:
        next_text, is_complete = _ai_engine.ask_next_question(ctx)
    except Exception as e:
        logger.error("AI Engine error: %s", e)
        await message.answer(
            "⚠️ Произошла ошибка при обращении к AI. Попробуйте ещё раз."
        )
        return

    # Обновляем данные в FSM
    await state.update_data(
        interview_answers=ctx.answers,
        question_count=ctx.question_count,
        last_question=next_text if not is_complete else "",
    )

    if is_complete or ctx.question_count >= 5:
        # ── Достаточно данных → Генерируем промт ─────────
        await state.set_state(InterviewStates.generating)
        await message.answer("⏳ Генерирую профессиональный промт...")

        await message.bot.send_chat_action(message.chat.id, "typing")

        try:
            prompt = _ai_engine.generate_prompt(ctx)
        except Exception as e:
            logger.error("Prompt generation error: %s", e)
            await message.answer("⚠️ Ошибка генерации промта. Попробуйте /start заново.")
            await state.clear()
            return

        # Подбираем рекомендации
        skills, mcps = _recommender.recommend(
            category=data.get("category", ""),
            subcategory=data.get("subcategory", ""),
            task_type=data.get("task_type", ""),
            summary=next_text,
        )

        # Сохраняем результат в стейт для возможного уточнения
        prompt_data = {
            "role": prompt.role,
            "task": prompt.task,
            "context": prompt.context,
            "constraints": prompt.constraints,
            "format": prompt.format,
        }
        await state.update_data(
            generated_prompt=prompt_data,
            recommended_skills=skills,
            recommended_mcps=mcps,
        )
        await state.set_state(InterviewStates.result_ready)

        # ── Отправляем результат ─────────────────────────
        # Блок 1: Промт
        prompt_text = format_prompt_result(prompt_data)
        await message.answer(text=prompt_text, parse_mode="MarkdownV2")

        # Блок 2: Рекомендации
        if skills or mcps:
            rec_text = format_recommendations(skills, mcps)
            await message.answer(text=rec_text, parse_mode="MarkdownV2")

        # Блок 3: Кнопки действий
        await message.answer(
            text="Что делаем дальше?",
            reply_markup=build_result_actions_keyboard(),
        )

    else:
        # ── Нужен ещё вопрос ─────────────────────────────
        await message.answer(next_text)


# ═══════════════════════════════════════════════════════════
#  Действия с результатом
# ═══════════════════════════════════════════════════════════


@router.callback_query(InterviewStates.result_ready, F.data == "action:refine")
async def on_refine(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь хочет уточнить промт."""
    await state.set_state(InterviewStates.refining)
    await callback.message.edit_text(
        text="✏️ Что хотите изменить в промте?",
        reply_markup=build_refine_keyboard(),
    )
    await callback.answer()


@router.callback_query(InterviewStates.result_ready, F.data == "action:restart")
async def on_restart(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать заново."""
    from bot.keyboards.categories import build_categories_keyboard

    await state.clear()
    await state.set_state(InterviewStates.choosing_category)
    await callback.message.edit_text(
        text="🎯 Выберите сферу деятельности:",
        reply_markup=build_categories_keyboard(),
    )
    await callback.answer()


@router.callback_query(InterviewStates.result_ready, F.data.startswith("action:rate:"))
async def on_rate(callback: CallbackQuery, state: FSMContext) -> None:
    """Оценка результата."""
    rating = callback.data.split(":")[2]
    await callback.answer(f"Спасибо за оценку {rating}/5! ⭐", show_alert=True)


# ═══════════════════════════════════════════════════════════
#  Уточнение промта
# ═══════════════════════════════════════════════════════════


@router.callback_query(InterviewStates.refining, F.data.startswith("refine:"))
async def on_refine_section(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь выбрал секцию для уточнения."""
    section = callback.data.split(":")[1]

    if section == "done":
        # Вернуться к результату
        await state.set_state(InterviewStates.result_ready)
        await callback.message.edit_text(
            text="✅ Промт готов! Что делаем дальше?",
            reply_markup=build_result_actions_keyboard(),
        )
        await callback.answer()
        return

    section_names = {
        "role": "роль",
        "task": "задачу",
        "context": "контекст",
        "format": "формат",
    }
    section_name = section_names.get(section, section)

    await state.update_data(refining_section=section)
    await callback.message.edit_text(f"Напишите новую {section_name} или уточнение:")
    await callback.answer()


@router.message(InterviewStates.refining)
async def on_refine_text(message: Message, state: FSMContext) -> None:
    """Пользователь прислал уточнение для конкретной секции."""
    data = await state.get_data()
    section = data.get("refining_section", "task")
    prompt_data: dict = data.get("generated_prompt", {})

    # Обновляем секцию
    prompt_data[section] = message.text or prompt_data.get(section, "")
    await state.update_data(generated_prompt=prompt_data)
    await state.set_state(InterviewStates.result_ready)

    # Отправляем обновлённый промт
    prompt_text = format_prompt_result(prompt_data)
    await message.answer(text=prompt_text, parse_mode="MarkdownV2")
    await message.answer(
        text="Что делаем дальше?",
        reply_markup=build_result_actions_keyboard(),
    )
