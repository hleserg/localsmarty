# Техническое задание: Telegram-бот с интеграцией YandexGPT (Yandex Cloud)

Дата: 06.09.2025

## 1. Цель

Создать простого Telegram-бота, который ведёт диалог с пользователем, генерируя ответы с помощью актуальной модели YandexGPT, размещённой в Yandex Cloud Foundation Models. Бот должен быть разворачиваемым локально (polling) и в контейнере (Docker). Конфигурация — через переменные окружения.

## 2. Область применения

- Частные чаты и групповые чаты Telegram.
- Русский и английский языки диалога.

## 3. Функциональные требования

1. Команды:
   - /start — приветствие и краткая подсказка.
   - /help — список команд и описание возможностей.
2. Обработка обычных текстовых сообщений:
   - Пересылка сообщения пользователя в YandexGPT Chat API.
   - Возврат текста ответа пользователю.
3. Контекст диалога (минимальный):
   - Хранить 5–20 последних сообщений в оперативной памяти для одного чата (per chat_id) для лучшего качества ответов.
   - Возможность отключить контекст (переменная окружения: ENABLE_CONTEXT=false).
4. Ограничения:
   - Максимальная длина входного сообщения: 4000 символов (Telegram лимит) — валидировать и сообщать об усечении.
   - Таймаут запроса к YandexGPT: 30 секунд по умолчанию, настраиваемый.
5. Логирование:
   - INFO — основные события; ERROR — ошибки API и сети.
   - Маскирование секретов в логах.
6. Диагностика:
   - Команда /ping — проверка живости бота (возвращает pong и версию).

7. Прикольная фишка — голосовой режим (опционально, включается флагом):

- При получении голосового сообщения (voice/audio) бот распознаёт речь через SpeechKit STT, передаёт распознанный текст в YandexGPT и возвращает ответ.
- Режим ответа: текстом по умолчанию; при включённой опции TTS — дополнительно отправлять голосовой ответ, синтезированный через SpeechKit TTS.
- Ограничения: длительность входного аудио до 60 секунд; поддержка русского и английского.

## 4. Нефункциональные требования

- Язык: Python 3.10+.
- Библиотека бота: python-telegram-bot v13+ или v20+ (выбрать и зафиксировать; предпочтительно v20+).
- HTTP-клиент: requests или httpx; поддержка ретраев с экспоненциальной паузой.
- Качество кода: типизация, pydantic-модели DTO, линтинг (ruff/flake8) — по возможности.
- Тесты: базовые unit-тесты для клиента YandexGPT и обработчика сообщений.

- Для голосового режима:
  - Поддержка форматов OGG/Opus из Telegram (без конвертации) для STT.
  - Для локальной конвертации (если потребуется): наличие `ffmpeg` (опционально).
  - Выходной голосовой ответ — формат `oggopus` (поддерживается Telegram).

## 5. Интеграция с Yandex Cloud Foundation Models

Актуальная схема (согласно документации):

- Базовый REST endpoint: <https://llm.api.cloud.yandex.net/foundationModels/v1/>
- Метод чата (completion): POST `/chat/completion`
- Заголовки:
  - `Authorization: Bearer <IAM_TOKEN>` или `Authorization: Api-Key <API_KEY>`
  - `x-folder-id: <FOLDER_ID>`
  - `Content-Type: application/json`
- Модель указывается через `modelUri`:
  - Формат: `gpt://CATALOG_ID/yandexgpt/latest`
  - Для Pro-версии: `gpt://CATALOG_ID/yandexgpt-pro/latest`
  - Для lite: `gpt://CATALOG_ID/yandexgpt-lite/latest`
- Тело запроса (пример):

```json
{
  "modelUri": "gpt://CATALOG_ID/yandexgpt/latest",
  "completionOptions": {
    "stream": false,
    "temperature": 0.3,
    "maxTokens": 800
  },
  "messages": [
    {"role": "system", "text": "Ты — полезный Telegram-бот."},
    {"role": "user", "text": "Привет!"}
  ]
}
```

- Ответ (фрагмент): `result.alternatives[0].message.text`
- Стриминг: при `stream=true` ответы приходят как поток событий (SSE) — опционально.

Примечание: В текущем репозитории используются устаревшие поля `model` и старый endpoint; требуется обновление под Foundation Models API.

### Интеграция с SpeechKit (STT/TTS) для голосового режима

- STT (распознавание речи):
  - Endpoint: <https://stt.api.cloud.yandex.net/speech/v1/stt:recognize>
  - Метод: `POST`
  - Аутентификация: `Authorization: Api-Key <API_KEY>` или `Authorization: Bearer <IAM_TOKEN>`
  - Параметры (query/form): `folderId=FOLDER_ID`, `lang=ru-RU|en-US`, опционально `topic=general`, `profanityFilter=true|false`.
  - Тело: бинарные данные аудио (`audio/ogg` с кодеком Opus из Telegram) или `application/octet-stream`.
  - Ответ: JSON с полем `result` (распознанный текст).

- TTS (синтез речи):
  - Endpoint: <https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize>
  - Метод: `POST`
  - Аутентификация: `Authorization: Api-Key <API_KEY>` или `Authorization: Bearer <IAM_TOKEN>`
  - Content-Type: `application/x-www-form-urlencoded`
  - Параметры: `text=...`, `voice=alena|filipp|...`, `lang=ru-RU|en-US`, `format=oggopus`, `speed=1.0` и др.
  - Ответ: бинарный поток аудио (`audio/ogg`).

Ссылки:

- STT: <https://yandex.cloud/ru/docs/speechkit/stt/request>
- TTS: <https://yandex.cloud/ru/docs/speechkit/tts/request>

## 6. Аутентификация и безопасность

- Использовать IAM-токен сервисного аккаунта (SA) Yandex Cloud или постоянный API-ключ (предпочтительно для серверного сценария).
- Переменные окружения:
  - `TELEGRAM_TOKEN` — токен Telegram-бота.
  - `YC_FOLDER_ID` — ID каталога Yandex Cloud.
  - `YC_IAM_TOKEN` — IAM-токен (регулярно обновлять; срок жизни ~12 часов) — если выбран Bearer.
  - `YC_API_KEY` — API-ключ сервисного аккаунта — если выбран Api-Key.
  - `YC_MODEL_URI` — явная строка modelUri (если не задана — формировать из `YC_FOLDER_ID` и суффикса модели).
  - `YC_TEMPERATURE`, `YC_MAX_TOKENS` — настройки генерации.
  - `ENABLE_CONTEXT` — true/false.
  - `LOG_LEVEL` — уровень логов.
- Для голосового режима:
  - `ENABLE_VOICE` — включить голосовой режим (true/false).
  - `STT_LANGUAGE` — язык распознавания, например `ru-RU`.
  - `TTS_VOICE` — голос, например `alena` (ru) или `filipp`.
  - `TTS_FORMAT` — `oggopus` (рекомендовано для Telegram).
  - `AUDIO_MAX_DURATION_SEC` — максимальная длительность входного аудио (по умолчанию 60).
- Никогда не писать токены в логи.

## 7. Пошаговая настройка в консоли Яндекс Облака

1. Создать каталог (Folder) или выбрать существующий. Сохранить `Folder ID`.

1. Создать сервисный аккаунт (SA) и назначить роли: `ai.languageModels.user` (доступ к Foundation Models), `viewer` (по необходимости), а также роли для SpeechKit (STT/TTS) согласно документации SpeechKit (права на распознавание и синтез).

1. Получить учётные данные для запросов к API:
   - Вариант A (Api-Key — проще):
     - Создать API-ключ для SA: `yc iam api-key create --service-account-id <SA_ID>`
     - Использовать заголовок `Authorization: Api-Key <API_KEY>` в запросах.
   - Вариант B (Bearer IAM):
     - Получить IAM-токен: `yc iam create-token` (для текущего пользователя) или программно обменять ключ SA на IAM.
     - Использовать заголовок `Authorization: Bearer <IAM_TOKEN>` в запросах.
1. Включить доступ к Foundation Models (если требуется по аккаунту/квоте).

1. Проверить лимиты и квоты в разделе Foundation Models.

1. Для голосового режима убедиться, что SpeechKit активен, и квоты/лимиты достаточны для STT/TTS.

Ссылки в документации:

- Обзор: <https://yandex.cloud/ru/docs/foundation-models/>
- Chat API (completion): <https://yandex.cloud/ru/docs/foundation-models/llm/api-ref/Chat/completion>
- Модели: <https://yandex.cloud/ru/docs/foundation-models/concepts/yandexgpt/models>
- Безопасность и роли: <https://yandex.cloud/ru/docs/foundation-models/security/>

## 8. Изменения в кодовой базе (миграция на FM API)

Требуется:

- Обновить `src/config.py`:
  - Удалить старые поля `YANDEX_MODEL`, `YANDEX_ENDPOINT`.
  - Добавить `YC_FOLDER_ID`, `YC_MODEL_URI`, `YC_TEMPERATURE`, `YC_MAX_TOKENS`, `YC_API_KEY`/`YC_IAM_TOKEN`.
  - `TELEGRAM_TOKEN` оставить.
- Переписать `src/services/yandex_client.py` на Foundation Models Chat API:
  - POST `https://llm.api.cloud.yandex.net/foundationModels/v1/chat/completion`
  - Заголовки `Authorization` (Bearer или Api-Key), `x-folder-id`.
  - Тело с `messages` `[{role: system|user|assistant, text: str}]`, `completionOptions`.
  - Парсить ответ: `result.alternatives[0].message.text`.
- Привести `src/bot.py` и `src/handlers/commands.py` к единому клиенту, добавить поддержку контекста.
- В `.env.example` заменить `TOKEN` -> `TELEGRAM_TOKEN`, добавить `YC_*` переменные.
- В `requirements.txt` убрать `winston` (не Python) и при необходимости обновить версии.

- Голосовой режим:
  - Добавить клиент SpeechKit: `src/services/speech_client.py` (STT/TTS) или расширить `yandex_client.py` отдельными методами.
  - В обработчиках добавить хендлер для `voice`/`audio`: скачивание файла с Telegram, отправка в STT, прокидывание текста в GPT, возврат ответа (текст и/или аудио TTS).
  - Минимизировать зависимости: без конвертации аудио (использовать OGG/Opus напрямую). При необходимости — опционально `ffmpeg`.

## 9. Тесты

- Моки HTTP для Yandex API (`responses` или `httpx` + `respx`).
- Тест команды `/start` и текстового обработчика с простым сценарием.

- Голосовой режим:
  - Юнит-тест STT: корректная отправка аудио и разбор ответа.
  - Юнит-тест TTS: корректная сборка параметров и получение бинарного ответа.
  - Интеграционный тест обработчика `voice` с моками Telegram API.

## 10. Сборка и запуск

- Локально: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt && python src/bot.py`
- Docker: собрать образ и запустить с переменными окружения `TELEGRAM_TOKEN`, `YC_FOLDER_ID`, (`YC_IAM_TOKEN` или `YC_API_KEY`), `YC_MODEL_URI`.

- Для голосового режима (локально): при необходимости установить `ffmpeg` и убедиться, что Telegram аудио (OGG/Opus) корректно передаётся в STT.

## 11. Риски и ограничения

- Срок жизни IAM-токена — автоматическое обновление желательно (out of scope для MVP, можно вручную обновлять).
- Лимиты токенов модели и стоимость запросов — учесть в настройках температуры и `maxTokens`.

## 12. Готово, когда

- Бот отвечает в Telegram, используя YandexGPT через Foundation Models API.
- Пройдены 2 юнит-теста (клиент и обработчик).
- Документация в README обновлена.
