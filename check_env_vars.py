#!/usr/bin/env python3
"""
Скрипт для проверки переменных окружения в production
"""

import os
import requests

def check_environment_variables():
    """Проверяет все необходимые переменные окружения"""
    
    required_vars = {
        "TELEGRAM_BOT_TOKEN": "Токен телеграм бота от @BotFather",
        "OPENAI_API_KEY": "API ключ OpenAI для анализа медиа",
        "FACEBOOK_APP_ID": "ID приложения Facebook",
        "FACEBOOK_APP_SECRET": "Секрет приложения Facebook", 
        "RENDER": "Флаг production среды"
    }
    
    optional_vars = {
        "FACEBOOK_ACCESS_TOKEN": "Access токен Facebook",
        "FACEBOOK_AD_ACCOUNT_ID": "ID рекламного аккаунта",
        "DATABASE_URL": "URL базы данных",
        "MOCK_MODE": "Режим разработки"
    }
    
    print("🔍 Проверка переменных окружения...")
    print("=" * 50)
    
    missing_required = []
    
    # Проверяем обязательные переменные
    print("\n📋 ОБЯЗАТЕЛЬНЫЕ переменные:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Показываем только первые и последние символы для безопасности
            if len(value) > 10:
                masked_value = f"{value[:4]}...{value[-4:]}"
            else:
                masked_value = "***"
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: НЕ УСТАНОВЛЕНА - {description}")
            missing_required.append(var)
    
    # Проверяем опциональные переменные
    print("\n📋 ОПЦИОНАЛЬНЫЕ переменные:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if len(value) > 10:
                masked_value = f"{value[:4]}...{value[-4:]}"
            else:
                masked_value = "***"
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"⚠️  {var}: не установлена - {description}")
    
    print("\n" + "=" * 50)
    
    if missing_required:
        print(f"\n❌ КРИТИЧНО: Отсутствуют {len(missing_required)} обязательных переменных!")
        print("\n📝 Инструкция по установке переменных в Render.com:")
        print("1. Перейдите в дашборд Render.com")
        print("2. Выберите ваш сервис target-ai")
        print("3. Перейдите в раздел 'Environment'")
        print("4. Добавьте следующие переменные:")
        print()
        
        for var in missing_required:
            print(f"   {var} = [ваше_значение]")
        
        print("\n5. Нажмите 'Save Changes' для перезапуска сервиса")
        print("\n💡 Значения переменных можно взять из .env файла")
        
        return False
    else:
        print("\n✅ Все обязательные переменные настроены!")
        return True

def test_bot_token():
    """Тестирует токен телеграм бота"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("\n❌ TELEGRAM_BOT_TOKEN не установлен")
        return False
    
    print(f"\n🤖 Тестирование токена бота...")
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_data = bot_info["result"]
                print(f"✅ Бот активен: @{bot_data['username']} ({bot_data['first_name']})")
                return True
            else:
                print(f"❌ Ошибка API: {bot_info}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def check_server_health():
    """Проверяет здоровье сервера"""
    print(f"\n🏥 Проверка здоровья сервера...")
    
    try:
        response = requests.get(
            "https://target-ai-prlm.onrender.com/health",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервер работает: {data}")
            return True
        else:
            print(f"❌ Сервер недоступен: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения с сервером: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Диагностика Target AI")
    print("=" * 30)
    
    # Проверяем переменные окружения
    env_ok = check_environment_variables()
    
    # Тестируем токен бота
    bot_ok = test_bot_token()
    
    # Проверяем сервер
    server_ok = check_server_health()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТ ДИАГНОСТИКИ:")
    print(f"   Переменные окружения: {'✅' if env_ok else '❌'}")
    print(f"   Telegram бот токен: {'✅' if bot_ok else '❌'}")
    print(f"   Сервер: {'✅' if server_ok else '❌'}")
    
    if env_ok and bot_ok and server_ok:
        print("\n🎉 Всё готово к работе!")
        print("\n📱 Попробуйте отправить команду /start боту:")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            if response.status_code == 200:
                bot_info = response.json()["result"]
                print(f"   https://t.me/{bot_info['username']}")
    else:
        print("\n⚠️  Требуется настройка переменных окружения в Render.com")
