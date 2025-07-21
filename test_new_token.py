#!/usr/bin/env python3
"""
Тест нового токена Telegram бота
"""

import requests
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_new_token():
    """Тестирует новый токен"""
    new_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not new_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return False, None
        
    print("🧪 Тестирование нового токена...")
    print(f"Токен: {new_token[:15]}...")
    
    try:
        # Проверяем токен через getMe
        response = requests.get(
            f"https://api.telegram.org/bot{new_token}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_data = bot_info["result"]
                print(f"✅ Новый токен работает!")
                print(f"   Имя бота: {bot_data['first_name']}")
                print(f"   Username: @{bot_data['username']}")
                print(f"   ID: {bot_data['id']}")
                return True, bot_data
            else:
                print(f"❌ Ошибка API: {bot_info}")
                return False, None
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False, None

def check_old_token():
    """Проверяет что старый токен отозван"""
    old_token = "8137758490:AAEkDpQ9i5Y_Ncr7DE52nIjLai2XWXOeu7E"
    
    print("\n🔒 Проверка старого токена...")
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{old_token}/getMe",
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Старый токен корректно отозван")
            return True
        elif response.status_code == 200:
            print("⚠️ Старый токен всё ещё активен! Отзовите его через @BotFather")
            return False
        else:
            print(f"❓ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def test_bot_integration():
    """Тестирует интеграцию с новым токеном"""
    print("\n🔧 Тестирование интеграции...")
    
    new_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not new_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return False
    
    try:
        from telegram.ext import Application, CommandHandler
        
        # Простой обработчик
        async def test_start(update, context):
            await update.message.reply_text("🎉 Новый токен работает!")
        
        # Создаем приложение с новым токеном
        app = Application.builder().token(new_token).build()
        app.add_handler(CommandHandler("start", test_start))
        
        # Тестируем инициализацию
        await app.initialize()
        await app.start()
        
        print("✅ Интеграция работает с новым токеном")
        
        # Останавливаем
        await app.stop()
        await app.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Проверка нового токена Telegram бота")
    print("=" * 50)
    
    # Тестируем новый токен
    token_ok, bot_info = test_new_token()
    
    # Проверяем старый токен
    old_revoked = check_old_token()
    
    # Тестируем интеграцию
    if token_ok:
        integration_ok = asyncio.run(test_bot_integration())
    else:
        integration_ok = False
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТ:")
    print(f"   Новый токен: {'✅' if token_ok else '❌'}")
    print(f"   Старый токен отозван: {'✅' if old_revoked else '❌'}")
    print(f"   Интеграция: {'✅' if integration_ok else '❌'}")
    
    if token_ok and old_revoked and integration_ok:
        print("\n🎉 Всё готово!")
        print("\n📝 Следующие шаги:")
        print("1. Обновите TELEGRAM_BOT_TOKEN в Render.com")
        print(f"   Новое значение: [используйте токен из .env]")
        print("2. Подождите перезапуска сервиса")
        print("3. Протестируйте бота в Telegram")
        print(f"4. Ссылка на бота: https://t.me/{bot_info['username'] if bot_info else 'aidigitaltarget_bot'}")
    else:
        print("\n⚠️ Требуются дополнительные действия")
        if not old_revoked:
            print("   - Отзовите старый токен через @BotFather")
        if not token_ok:
            print("   - Проверьте новый токен")
        if not integration_ok:
            print("   - Исправьте проблемы интеграции")
