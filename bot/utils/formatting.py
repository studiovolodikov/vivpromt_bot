"""Утилиты форматирования Markdown для Telegram."""


def format_prompt_result(prompt_data: dict) -> str:
    """Форматирование финального промта для отправки в Telegram.

    Args:
        prompt_data: Словарь с ключами role, task, context, constraints, format.

    Returns:
        Отформатированная Markdown-строка.
    """
    sections = []
    section_icons = {
        "role": "🎭 *Роль:*",
        "task": "📋 *Задача:*",
        "context": "📐 *Контекст:*",
        "constraints": "⚙️ *Ограничения:*",
        "format": "📄 *Формат ответа:*",
    }

    for key, header in section_icons.items():
        value = prompt_data.get(key, "")
        if value:
            sections.append(f"{header}\n{escape_md(value)}")

    prompt_body = "\n\n".join(sections)

    return (
        "📝 *ВАШИ ПРОМТ*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{prompt_body}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )


def format_recommendations(skills: list[dict], mcps: list[dict]) -> str:
    """Форматирование рекомендаций Skills и MCP.

    Args:
        skills: Список рекомендованных Skills.
        mcps: Список рекомендованных MCP-серверов.

    Returns:
        Отформатированная Markdown-строка.
    """
    lines = [
        "🛠️ *РЕКОМЕНДУЕМЫЕ ИНСТРУМЕНТЫ*",
        "━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    if skills:
        lines.append("📦 *Skills \\(Навыки\\):*")
        for i, skill in enumerate(skills, 1):
            priority_icon = "🟢" if skill.get("priority") == "high" else "🟡"
            name = escape_md(skill.get("name", ""))
            desc = escape_md(skill.get("description", ""))
            lines.append(f"  {i}\\. {priority_icon} `{name}` — {desc}")
        lines.append("")

    if mcps:
        lines.append("🔌 *MCP\\-серверы:*")
        for i, mcp in enumerate(mcps, 1):
            priority_icon = "🟢" if mcp.get("priority") == "high" else "🟡"
            name = escape_md(mcp.get("name", ""))
            desc = escape_md(mcp.get("description", ""))
            lines.append(f"  {i}\\. {priority_icon} `{name}` — {desc}")
        lines.append("")

    lines.append("🟢 \\= Критически важно  \\|  🟡 \\= Рекомендуется")

    return "\n".join(lines)


def escape_md(text: str) -> str:
    """Экранирование спецсимволов для MarkdownV2.

    Telegram MarkdownV2 требует экранирования: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    special_chars = r"_*[]()~`>#+-=|{}.!"
    result = []
    for char in text:
        if char in special_chars:
            result.append(f"\\{char}")
        else:
            result.append(char)
    return "".join(result)
