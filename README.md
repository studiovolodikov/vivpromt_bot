# 🎯 Prompt Strategist Bot

Telegram-бот для генерации профессиональных промтов с AI-интервью и рекомендацией Skills и MCP-серверов.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполните переменные в `.env`:
- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather)
- `GROQ_API_KEY` — API-ключ от [Groq Console](https://console.groq.com/keys)

### 3. Запуск

```bash
# Локально
python -m bot.main

# Docker
docker compose up -d
```

## 📂 Структура проекта

```
prompt-strategist-bot/
├── bot/
│   ├── main.py           # Точка входа
│   ├── config.py         # Конфигурация
│   ├── handlers/         # Обработчики
│   │   ├── start.py      # /start
│   │   ├── category.py   # Выбор категории
│   │   └── interview.py  # AI-интервью
│   ├── keyboards/        # Inline-клавиатуры
│   ├── middleware/       # Rate limiting
│   ├── states/           # FSM-состояния
│   └── utils/            # Форматирование
├── core/
│   ├── ai_engine.py      # Groq API (groq/compound)
│   └── recommender.py    # Рекомендации
├── data/
│   ├── skills_catalog.json
│   └── mcp_catalog.json
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🤖 Как работает

1. **Выбор категории** — 6 сфер, 20+ подкатегорий
2. **AI-интервью** — 2-5 уточняющих вопросов (groq/compound)
3. **Генерация промта** — Role, Task, Context, Constraints, Format
4. **Рекомендации** — Skills и MCP-серверы

## ⚙️ Конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram-бота | — |
| `GROQ_API_KEY` | API-ключ Groq | — |
| `GROQ_MODEL` | Модель Groq | `groq/compound` |
| `RATE_LIMIT_PER_MINUTE` | Лимит запросов | `10` |
| `LOG_LEVEL` | Уровень логов | `INFO` |

## 🛠️ Технологии

- **Python 3.10+**
- **aiogram 3.x** — Telegram-бот
- **Groq API** — groq/compound (модель с рассуждениями)
- **Docker** — контейнеризация

## 📦 Docker

```bash
docker compose up -d
docker compose logs -f bot
```

## 📝 Лицензия

MIT
