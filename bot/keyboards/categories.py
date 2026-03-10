"""Inline-клавиатуры для выбора категорий и подкатегорий."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ═══════════════════════════════════════════════════════════
#  ДЕРЕВО КАТЕГОРИЙ
# ═══════════════════════════════════════════════════════════

CATEGORIES: dict[str, dict] = {
    "dev": {
        "label": "💻 Разработка",
        "subcategories": {
            "backend": {"label": "⚙️ Backend", "tasks": ["write", "design", "debug", "optimize", "review"]},
            "frontend": {"label": "🎨 Frontend", "tasks": ["write", "design", "debug", "optimize", "review"]},
            "devops": {"label": "🚀 DevOps", "tasks": ["configure", "deploy", "monitor", "automate"]},
            "mobile": {"label": "📱 Mobile", "tasks": ["write", "design", "debug", "optimize"]},
            "ai_ml": {"label": "🤖 AI / ML", "tasks": ["train", "design", "optimize", "integrate"]},
            "database": {"label": "🗄️ Database", "tasks": ["design", "optimize", "migrate", "query"]},
        },
    },
    "marketing": {
        "label": "📈 Маркетинг",
        "subcategories": {
            "content": {"label": "✍️ Контент", "tasks": ["write", "optimize", "plan"]},
            "seo": {"label": "🔍 SEO", "tasks": ["audit", "optimize", "research"]},
            "smm": {"label": "📱 SMM", "tasks": ["create", "plan", "analyze"]},
            "email": {"label": "📧 Email", "tasks": ["write", "design", "automate"]},
            "ads": {"label": "💰 Реклама", "tasks": ["create", "optimize", "analyze"]},
        },
    },
    "design": {
        "label": "🎨 Дизайн",
        "subcategories": {
            "ui_ux": {"label": "📐 UI/UX", "tasks": ["design", "audit", "prototype"]},
            "graphic": {"label": "🖼️ Графика", "tasks": ["create", "edit", "brand"]},
            "web_design": {"label": "🌐 Веб-дизайн", "tasks": ["design", "redesign", "audit"]},
        },
    },
    "business": {
        "label": "💼 Бизнес",
        "subcategories": {
            "strategy": {"label": "📊 Стратегия", "tasks": ["plan", "analyze", "research"]},
            "sales": {"label": "🤝 Продажи", "tasks": ["script", "analyze", "optimize"]},
            "analytics": {"label": "📉 Аналитика", "tasks": ["report", "forecast", "dashboard"]},
        },
    },
    "writing": {
        "label": "📝 Тексты",
        "subcategories": {
            "copywriting": {"label": "✏️ Копирайтинг", "tasks": ["write", "edit", "translate"]},
            "technical": {"label": "📖 Тех. документация", "tasks": ["write", "review", "structure"]},
            "creative": {"label": "🎭 Креатив", "tasks": ["write", "brainstorm", "rewrite"]},
        },
    },
    "education": {
        "label": "🎓 Обучение",
        "subcategories": {
            "course": {"label": "📚 Курсы", "tasks": ["create", "structure", "lesson"]},
            "research": {"label": "🔬 Исследование", "tasks": ["analyze", "summarize", "compare"]},
        },
    },
}

# ── Маппинг типов задач на человекочитаемые лейблы ─────────
TASK_TYPE_LABELS: dict[str, str] = {
    "write": "✍️ Написать код",
    "design": "📐 Спроектировать",
    "debug": "🐛 Отладить",
    "optimize": "⚡ Оптимизировать",
    "review": "👁️ Ревью",
    "configure": "🔧 Настроить",
    "deploy": "🚀 Развернуть",
    "monitor": "📊 Мониторинг",
    "automate": "🤖 Автоматизировать",
    "train": "🧠 Обучить модель",
    "integrate": "🔗 Интегрировать",
    "migrate": "🔄 Мигрировать",
    "query": "🔍 Запрос / Выборка",
    "audit": "🔎 Аудит",
    "research": "🔬 Исследование",
    "create": "🆕 Создать",
    "plan": "📋 Составить план",
    "analyze": "📉 Проанализировать",
    "edit": "✂️ Отредактировать",
    "prototype": "🧩 Прототип",
    "brand": "🏷️  Брендинг",
    "redesign": "♻️ Редизайн",
    "script": "📜 Скрипт продаж",
    "report": "📝 Отчёт",
    "forecast": "🔮 Прогноз",
    "dashboard": "📊 Дашборд",
    "translate": "🌐 Перевод",
    "structure": "🏗️ Структурировать",
    "brainstorm": "💡 Брейнсторм",
    "rewrite": "🔁 Переписать",
    "lesson": "📖 Урок",
    "summarize": "📋 Резюме",
    "compare": "⚖️ Сравнить",
}


# ═══════════════════════════════════════════════════════════
#  BUILDERS — Генераторы клавиатур
# ═══════════════════════════════════════════════════════════


def build_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура верхнего уровня: выбор сферы деятельности."""
    buttons = [
        [InlineKeyboardButton(text=data["label"], callback_data=f"cat:{key}")]
        for key, data in CATEGORIES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_subcategories_keyboard(category_key: str) -> InlineKeyboardMarkup | None:
    """Клавиатура подкатегорий для выбранной сферы."""
    category = CATEGORIES.get(category_key)
    if not category:
        return None

    buttons = [
        [InlineKeyboardButton(
            text=sub_data["label"],
            callback_data=f"sub:{category_key}:{sub_key}",
        )]
        for sub_key, sub_data in category["subcategories"].items()
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_task_types_keyboard(category_key: str, subcategory_key: str) -> InlineKeyboardMarkup | None:
    """Клавиатура типов задач для подкатегории."""
    category = CATEGORIES.get(category_key)
    if not category:
        return None

    subcategory = category["subcategories"].get(subcategory_key)
    if not subcategory:
        return None

    buttons = [
        [InlineKeyboardButton(
            text=TASK_TYPE_LABELS.get(task, task),
            callback_data=f"task:{category_key}:{subcategory_key}:{task}",
        )]
        for task in subcategory["tasks"]
    ]
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=f"back:sub:{category_key}",
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
