FROM python:3.11-slim

WORKDIR /app

# Установим системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установим зависимости Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем исходный код в контейнер
COPY src/ /app/src/
COPY set_webhook.py /app/set_webhook.py
COPY .env.example /app/.env

# Создаем директории для логов и SSL
RUN mkdir -p /app/logs /app/ssl

# Определяем команду для запуска бота
WORKDIR /app/src

# По умолчанию запускаем webhook сервер
CMD ["python", "webhook_server.py"]