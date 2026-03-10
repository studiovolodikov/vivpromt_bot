FROM python:3.12-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Приложение
COPY bot/ bot/
COPY core/ core/
COPY data/ data/

# Запуск
CMD ["python", "-m", "bot.main"]
