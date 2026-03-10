"""AI Engine — Мозг системы.

Управляет взаимодействием с Groq API (DeepSeek-R1) для проведения интервью
и генерации финального промта.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from groq import Groq

from bot.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  Модели данных
# ═══════════════════════════════════════════════════════════


@dataclass
class InterviewContext:
    """Контекст текущего интервью пользователя."""

    category: str = ""
    subcategory: str = ""
    task_type: str = ""
    answers: list[dict[str, str]] = field(default_factory=list)
    question_count: int = 0
    is_complete: bool = False

    def to_summary(self) -> str:
        """Сводка всех ответов для передачи в LLM."""
        lines = [
            f"Категория: {self.category}",
            f"Подкатегория: {self.subcategory}",
            f"Тип задачи: {self.task_type}",
        ]
        for qa in self.answers:
            lines.append(f"В: {qa['question']}")
            lines.append(f"О: {qa['answer']}")
        return "\n".join(lines)


@dataclass
class GeneratedPrompt:
    """Результат генерации промта."""

    role: str = ""
    task: str = ""
    context: str = ""
    constraints: str = ""
    format: str = ""
    raw_text: str = ""


# ═══════════════════════════════════════════════════════════
#  AI Engine
# ═══════════════════════════════════════════════════════════


INTERVIEW_SYSTEM_PROMPT = """Ты — эксперт-архитектор промтов. Твоя задача — провести интервью с пользователем,
чтобы собрать всю необходимую информацию для генерации идеального промта.

ПРАВИЛА:
1. Задавай ОДИН вопрос за раз
2. Вопросы должны быть краткими и конкретными
3. Предлагай варианты ответов где возможно (в формате 1), 2), 3))
4. Когда информации достаточно — ответь JSON-объектом с ключом "complete": true
5. Обычно достаточно 2-4 вопроса
6. Учитывай уже известный контекст (категория, подкатегория, тип задачи)

Контекст пользователя:
{context}

Если у тебя достаточно информации, верни JSON:
{{"complete": true, "summary": "краткое описание задачи"}}

Иначе задай следующий вопрос (просто текст вопроса, без JSON).
"""

GENERATION_SYSTEM_PROMPT = """Ты — ведущий мировой специалист по созданию промтов для ИИ.
Сгенерируй профессиональный, структурированный промт на основе собранной информации.

СТРОГИЙ ФОРМАТ ОТВЕТА — JSON:
{{
    "role": "Детальное описание роли ИИ (кто он, его экспертиза, опыт)",
    "task": "Чёткая, конкретная задача с ожидаемым результатом",
    "context": "Весь релевантный контекст: стек технологий, среда, ограничения",
    "constraints": "Технические и бизнес-ограничения, что делать НЕ нужно",
    "format": "Точный формат ожидаемого ответа (код, документ, список, таблица и т.д.)"
}}

ТРЕБОВАНИЯ К КАЧЕСТВУ:
- Роль должна быть максимально экспертной и специфичной (не \"программист\", а \"Senior Backend Engineer с 10+ годами опыта в Node.js, TypeScript, PostgreSQL\")
- Задача должна быть однозначной и измеримой
- Контекст должен содержать ВСЮ необходимую информацию
- Ответ ТОЛЬКО в формате JSON, без markdown-обёртки

Собранная информация:
{context}
"""


class AIEngine:
    """Движок для взаимодействия с Groq API."""

    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    def ask_next_question(self, ctx: InterviewContext) -> tuple[str, bool]:
        """Получить следующий вопрос интервью или сигнал о завершении.

        Returns:
            Кортеж (текст_вопроса_или_summary, is_complete).
        """
        system = INTERVIEW_SYSTEM_PROMPT.format(context=ctx.to_summary())
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": "Задай следующий уточняющий вопрос или сообщи что данных достаточно.",
            },
        ]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        content = response.choices[0].message.content or ""
        logger.info("AI response: %s", content[:200])

        # Проверяем, вернул ли AI JSON с complete: true
        try:
            data = json.loads(content)
            if data.get("complete"):
                return data.get("summary", ""), True
        except (json.JSONDecodeError, TypeError):
            pass

        return content, False

    def generate_prompt(self, ctx: InterviewContext) -> GeneratedPrompt:
        """Сгенерировать финальный промт на основе собранного контекста.

        Returns:
            GeneratedPrompt с заполненными полями.
        """
        system = GENERATION_SYSTEM_PROMPT.format(context=ctx.to_summary())
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": "Сгенерируй промт. Ответ СТРОГО в формате JSON.",
            },
        ]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.4,
            max_tokens=1500,
        )

        content = response.choices[0].message.content or "{}"
        logger.info("Generated prompt JSON: %s", content[:300])

        # Извлекаем JSON из ответа (модель может обернуть в ```json ... ```)
        clean_content = content.strip()
        if clean_content.startswith("```"):
            lines = clean_content.split("\n")
            json_lines = [l for l in lines if not l.strip().startswith("```")]
            clean_content = "\n".join(json_lines)

        try:
            data = json.loads(clean_content)
        except json.JSONDecodeError:
            logger.error("Failed to parse prompt JSON: %s", content)
            return GeneratedPrompt(raw_text=content)

        return GeneratedPrompt(
            role=data.get("role", ""),
            task=data.get("task", ""),
            context=data.get("context", ""),
            constraints=data.get("constraints", ""),
            format=data.get("format", ""),
            raw_text=content,
        )
