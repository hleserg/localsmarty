@echo off
echo 🤖 Установка webhook для Telegram бота
echo ======================================

REM Проверяем наличие .env файла
if not exist .env (
    echo ❌ Файл .env не найден. Создайте его из env.example
    echo    copy env.example .env
    echo    # Отредактируйте .env с вашими токенами
    pause
    exit /b 1
)

REM Загружаем переменные из .env (упрощенная версия)
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="TELEGRAM_TOKEN" set TELEGRAM_TOKEN=%%b
    if "%%a"=="WEBHOOK_URL" set WEBHOOK_URL=%%b
    if "%%a"=="WEBHOOK_PATH" set WEBHOOK_PATH=%%b
    if "%%a"=="WEBHOOK_SECRET_TOKEN" set WEBHOOK_SECRET_TOKEN=%%b
)

REM Проверяем обязательные переменные
if "%TELEGRAM_TOKEN%"=="" (
    echo ❌ TELEGRAM_TOKEN не установлен в .env файле
    pause
    exit /b 1
)

if "%WEBHOOK_URL%"=="" (
    echo ❌ WEBHOOK_URL не установлен в .env файле
    pause
    exit /b 1
)

if "%WEBHOOK_PATH%"=="" (
    echo ❌ WEBHOOK_PATH не установлен в .env файле
    pause
    exit /b 1
)

REM Формируем параметры
set WEBHOOK_FULL_URL=%WEBHOOK_URL%%WEBHOOK_PATH%
set ALLOWED_UPDATES=["message","edited_message","business_connection","business_message","edited_business_message","deleted_business_messages"]

echo 🔗 Webhook URL: %WEBHOOK_FULL_URL%
echo 📋 Allowed updates: %ALLOWED_UPDATES%

REM Формируем URL для установки webhook
set API_URL=https://api.telegram.org/bot%TELEGRAM_TOKEN%/setWebhook

REM Параметры запроса
set PARAMS=url=%WEBHOOK_FULL_URL%&allowed_updates=%ALLOWED_UPDATES%

REM Добавляем secret_token если он есть
if not "%WEBHOOK_SECRET_TOKEN%"=="" (
    set PARAMS=%PARAMS%&secret_token=%WEBHOOK_SECRET_TOKEN%
    echo 🔐 Secret token: установлен
) else (
    echo ⚠️  Secret token: не установлен
)

echo.
echo 🚀 Устанавливаем webhook...

REM Отправляем запрос
powershell -Command "try { $response = Invoke-RestMethod -Uri '%API_URL%?%PARAMS%' -Method Post; Write-Host '✅ Webhook успешно установлен!'; Write-Host '📊 Ответ:' $response } catch { Write-Host '❌ Ошибка установки webhook:' $_.Exception.Message }"

echo.
echo 🔍 Проверяем информацию о webhook...

REM Получаем информацию о webhook
set INFO_URL=https://api.telegram.org/bot%TELEGRAM_TOKEN%/getWebhookInfo
powershell -Command "try { $response = Invoke-RestMethod -Uri '%INFO_URL%' -Method Get; Write-Host '✅ Информация о webhook получена:'; $response | ConvertTo-Json -Depth 3 } catch { Write-Host '❌ Ошибка получения информации о webhook:' $_.Exception.Message }"

echo.
echo 🎉 Готово! Webhook установлен и настроен.
echo 📱 Теперь бот будет получать обновления через webhook.
pause
