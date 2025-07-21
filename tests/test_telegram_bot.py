import asyncio
import os
from dotenv import load_dotenv
from telegram_bot_v2 import start, button_callback, handle_media, BOT_TOKEN
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

async def test_bot_locally():
    """Тестирует бота локально"""
    print("🤖 Тестирование Telegram бота...")
    
    load_dotenv()
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return
    
    print(f"✅ Токен найден: {BOT_TOKEN[:10]}...")
    
    try:
        # Создаем приложение
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
        
        print("✅ Обработчики добавлены")
        
        # Инициализируем и проверяем подключение
        await app.initialize()
        print("✅ Бот инициализирован")
        
        # Получаем информацию о боте
        bot_info = await app.bot.get_me()
        print(f"✅ Подключение успешно!")
        print(f"   Имя бота: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        
        # Тестируем API соединение
        from telegram_bot_v2 import API_BASE_URL
        print(f"📡 API URL: {API_BASE_URL}")
        
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_BASE_URL}/health", timeout=5) as response:
                    if response.status == 200:
                        print("✅ API доступен")
                    else:
                        print(f"⚠️ API вернул статус: {response.status}")
        except Exception as e:
            print(f"❌ API недоступен: {e}")
        
        await app.shutdown()
        print("🎉 Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot_locally())
