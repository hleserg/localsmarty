#!/usr/bin/env python3
"""
Скрипт для запуска тестов Telegram бота.
Поддерживает различные режимы запуска и автоматически пропускает webhook тесты локально.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_webhook_environment():
    """Проверяет, настроен ли webhook для тестов"""
    webhook_url = os.getenv('WEBHOOK_URL', '')
    return (
        webhook_url and
        webhook_url.startswith('https://') and
        'localhost' not in webhook_url and
        '127.0.0.1' not in webhook_url
    )


def run_tests(marker=None, verbose=False, coverage=False, slow=False, webhook=False):
    """Запускает тесты с указанными параметрами"""
    cmd = ['python', '-m', 'pytest']
    
    # Добавляем маркер если указан
    if marker:
        cmd.extend(['-m', marker])
    
    # Добавляем verbose режим
    if verbose:
        cmd.append('-v')
    
    # Добавляем покрытие кода
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # Добавляем медленные тесты
    if slow:
        cmd.extend(['-m', 'slow'])
    
    # Проверяем webhook окружение
    if webhook:
        if not check_webhook_environment():
            print("⚠️  Webhook тесты пропущены - webhook не настроен для локальной среды")
            print("   Для запуска webhook тестов установите переменные окружения:")
            print("   - WEBHOOK_URL (должен быть HTTPS и не localhost)")
            print("   - WEBHOOK_PORT")
            print("   - WEBHOOK_PATH")
            print("   - WEBHOOK_SECRET_TOKEN")
            return False
        else:
            print("✅ Webhook окружение настроено, запускаем webhook тесты")
    else:
        print("ℹ️  Webhook тесты будут автоматически пропущены локально")
    
    # Запускаем тесты
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest не найден. Установите его командой: pip install pytest")
        return False


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Запуск тестов Telegram бота')
    
    parser.add_argument(
        '--marker', '-m',
        choices=['unit', 'integration', 'services', 'handlers', 'utils', 'config', 'models', 'webhook'],
        help='Запустить тесты с определенным маркером'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Показать покрытие кода'
    )
    
    parser.add_argument(
        '--slow',
        action='store_true',
        help='Включить медленные тесты'
    )
    
    parser.add_argument(
        '--webhook',
        action='store_true',
        help='Запустить webhook тесты (только на сервере)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Запустить все тесты включая медленные'
    )
    
    args = parser.parse_args()
    
    print("🚀 Запуск тестов Telegram бота")
    print("=" * 50)
    
    # Определяем параметры запуска
    marker = args.marker
    verbose = args.verbose
    coverage = args.coverage
    slow = args.slow or args.all
    webhook = args.webhook
    
    # Если не указан маркер, запускаем все тесты
    if not marker and not args.all:
        marker = None
    
    # Запускаем тесты
    success = run_tests(marker, verbose, coverage, slow, webhook)
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
        if coverage:
            print("📊 Отчет о покрытии создан в htmlcov/index.html")
    else:
        print("\n❌ Некоторые тесты не прошли")
        sys.exit(1)


if __name__ == '__main__':
    main()

