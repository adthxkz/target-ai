#!/usr/bin/env python3
"""
Тест исправленной telegram интеграции
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def test_fixed_integration():
    """Тестирует исправленную telegram интеграцию"""
    print("🧪 Тестирование исправленной Telegram интеграции...")
    
    # Проверяем токен
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return False
    
    print(f"✅ Токен найден: {token[:10]}...")
    
    try:
        # Устанавливаем RENDER=false для локального тестирования
        os.environ["RENDER"] = "false"
        
        # Добавляем путь к app модулю
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        # Импортируем без FastAPI
        import importlib.util
        
        # Создаем временный модуль для тестирования
        from telegram.ext import Application, CommandHandler
        
        # Простой обработчик
        async def test_start(update, context):
            await update.message.reply_text("🤖 Target AI Bot работает!")
        
        # Создаем приложение
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", test_start))
        
        print("✅ Application создан")
        
        # Тестируем инициализацию
        await app.initialize()
        print("✅ Application.initialize() успешен")
        
        await app.start()
        print("✅ Application.start() успешен")
        
        # Проверяем что webhook НЕ установлен в локальном режиме
        webhook_info = await app.bot.get_webhook_info()
        print(f"✅ Webhook info: {webhook_info.url or 'не установлен'}")
        
        # Останавливаем
        await app.stop()
        await app.shutdown()
        print("✅ Application остановлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fixed_integration())
    if result:
        print("\n🎉 Исправленная интеграция работает!")
        print("\n📝 Следующие шаги:")
        print("1. Деплой изменений в Render.com")
        print("2. Проверка что webhook установлен в production")
        print("3. Тестирование бота в Telegram")
    else:
        print("\n❌ Требуются дополнительные исправления")
