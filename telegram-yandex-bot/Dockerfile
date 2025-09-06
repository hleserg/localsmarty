FROM python:3.11-slim

WORKDIR /app

# Установим зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем исходный код в контейнер
COPY src/ /app/src/
COPY .env.example /app/.env

# Определяем команду для запуска бота
WORKDIR /app/src
CMD ["python", "bot.py"]