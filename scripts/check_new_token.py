#!/usr/bin/env python3
"""
Безопасная проверка нового токена Telegram бота
ВНИМАНИЕ: Токен должен быть установлен в переменных окружения!
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локального тестирования)
if os.path.exists(".env"):
    load_dotenv()

def check_new_token():
    """Проверяет новый токен из переменных окружения"""
    new_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print("🔍 Проверка нового токена Telegram бота...")
    print("=" * 50)
    
    if not new_token:
        print("❌ ОШИБКА: Токен не найден в переменных окружения!")
        print("   Установите TELEGRAM_BOT_TOKEN в .env или в Render.com")
        return False
    
    # Не показываем полный токен в логах
    token_preview = f"***{new_token[-10:]}" if len(new_token) > 10 else "***"
    print(f"📋 Найден токен: {token_preview}")
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{new_token}/getMe", timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print("✅ ТОКЕН РАБОТАЕТ КОРРЕКТНО!")
            print(f"   🤖 Бот: @{bot_info['username']}")
            print(f"   📝 Имя: {bot_info['first_name']}")
            print(f"   🆔 ID: {bot_info['id']}")
            print(f"   ⏰ Проверено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print(f"❌ ТОКЕН НЕ РАБОТАЕТ!")
            print(f"   Код ошибки: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА ПРОВЕРКИ ТОКЕНА: {e}")
        return False

def check_environment():
    """Проверяет настройки окружения"""
    print("\n🔧 Проверка переменных окружения...")
    print("=" * 50)
    
    env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'OPENAI_API_KEY', 
        'FACEBOOK_APP_ID',
        'FACEBOOK_APP_SECRET'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Показываем только последние 4 символа для безопасности
            preview = f"***{value[-4:]}" if len(value) > 4 else "***"
            print(f"   ✅ {var}: {preview}")
        else:
            print(f"   ❌ {var}: НЕ УСТАНОВЛЕНА")

def main():
    """Основная функция"""
    print("🔐 БЕЗОПАСНАЯ ПРОВЕРКА ТОКЕНА TELEGRAM БОТА")
    print("=" * 60)
    print(f"⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проверяем новый токен
    token_works = check_new_token()
    
    # Проверяем общие настройки
    check_environment()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ СТАТУС:")
    print("=" * 60)
    
    if token_works:
        print("✅ ВСЁ ГОТОВО! Новый токен работает корректно.")
        print("   Можно закрыть GitHub Security Alert.")
    else:
        print("❌ ТРЕБУЕТСЯ НАСТРОЙКА!")
        print("   1. Установите TELEGRAM_BOT_TOKEN в переменные окружения")
        print("   2. Перезапустите сервис в Render.com")
        print("   3. Повторите проверку")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
