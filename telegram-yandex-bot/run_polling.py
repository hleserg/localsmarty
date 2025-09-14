#!/usr/bin/env python3
"""
Запуск бота в режиме polling (для разработки)
"""

import os
import sys
from pathlib import Path

# Добавляем src в путь Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Импортируем и запускаем основной бот
from bot import main

if __name__ == "__main__":
    print("🔄 Запуск бота в режиме polling (для разработки)")
    print("📝 Для продакшена используйте webhook режим")
    print("-" * 50)
    main()
