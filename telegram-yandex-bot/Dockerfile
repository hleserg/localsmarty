FROM python:3.9-slim

# Установим необходимые зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код в контейнер
COPY src/ /app/src/
COPY .env.example /app/.env

# Устанавливаем рабочую директорию
WORKDIR /app/src

# Определяем команду для запуска бота
CMD ["python", "bot.py"]