#!/usr/bin/env python3
"""
Простой тест telegram bot без FastAPI зависимостей
"""

import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def test_telegram_bot_simple():
    """Простой тест telegram bot"""
    print("🧪 Простой тест Telegram Bot...")
    
    # Проверяем токен
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return False
    
    print(f"✅ Токен найден: {token[:10]}...")
    
    try:
        # Импортируем только telegram библиотеки
        from telegram.ext import Application, CommandHandler
        
        print("✅ telegram.ext импортирован")
        
        # Простой обработчик
        async def test_start(update, context):
            await update.message.reply_text("Test bot response!")
        
        # Создаем приложение
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", test_start))
        
        print("✅ Application создан с обработчиком")
        
        # Тестируем инициализацию
        await app.initialize()
        print("✅ Application.initialize() успешен")
        
        await app.start()
        print("✅ Application.start() успешен")
        
        # Не запускаем polling, только проверяем что всё инициализируется
        print("✅ Бот готов к работе (polling не запущен)")
        
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
    result = asyncio.run(test_telegram_bot_simple())
    if result:
        print("\n🎉 Telegram bot инициализация работает!")
        print("Проблема скорее всего в integration layer, а не в самом боте.")
    else:
        print("\n❌ Проблема в telegram bot setup")
