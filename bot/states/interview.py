"""FSM-состояния для процесса интервью."""

from aiogram.fsm.state import State, StatesGroup


class InterviewStates(StatesGroup):
    """Конечный автомат для пошагового интервью пользователя."""

    # ── Фаза 1: Быстрая навигация (Кнопки) ───────────────
    choosing_category = State()       # Выбор сферы: IT, Маркетинг, Дизайн...
    choosing_subcategory = State()    # Подкатегория: Backend, Frontend...
    choosing_task_type = State()      # Тип задачи: Написать, Спроектировать...

    # ── Фаза 2: AI-интервью ───────────────────────────────
    ai_interview = State()            # AI задаёт уточняющие вопросы

    # ── Фаза 3: Генерация и доставка ─────────────────────
    generating = State()              # Генерация промта (ожидание)
    result_ready = State()            # Результат готов, действия пользователя
    refining = State()                # Уточнение / доработка промта
