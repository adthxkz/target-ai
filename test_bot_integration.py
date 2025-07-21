#!/usr/bin/env python3
"""
Тест telegram bot интеграции с исправлениями
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к app модулю
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_bot_integration():
    """Тестирует новую версию telegram интеграции"""
    print("🧪 Тестирование Telegram Bot интеграции...")
    
    # Проверяем переменные окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return False
    
    print(f"✅ Токен найден: {token[:10]}...")
    
    try:
        # Импортируем telegram_integration
        from telegram_integration import TelegramBot
        
        print("✅ Модуль telegram_integration импортирован")
        
        # Создаем экземпляр бота
        bot = TelegramBot()
        print("✅ Экземпляр TelegramBot создан")
        
        # Пытаемся инициализировать (без polling)
        print("⏳ Инициализация бота...")
        
        # Проверяем, что мы можем создать Application
        from telegram.ext import Application
        test_app = Application.builder().token(token).build()
        
        print("✅ Application создан успешно")
        
        # Проверяем инициализацию
        await test_app.initialize()
        print("✅ Application.initialize() выполнен")
        
        # Останавливаем тест
        await test_app.shutdown()
        print("✅ Application.shutdown() выполнен")
        
        print("\n🎉 Все проверки пройдены! Бот готов к работе.")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot_integration())
    if result:
        print("\n✅ Интеграция работает корректно")
    else:
        print("\n❌ Требуются исправления")
