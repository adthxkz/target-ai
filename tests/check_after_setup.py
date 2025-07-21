#!/usr/bin/env python3
"""
Скрипт для проверки статуса бота после настройки переменных окружения
"""

import requests
import time
import json

def check_bot_status():
    """Проверяет статус телеграм бота"""
    bot_token = "8137758490:AAEkDpQ9i5Y_Ncr7DE52nIjLai2XWXOeu7E"
    
    print("🤖 Проверка статуса Telegram бота...")
    
    try:
        # Получаем информацию о боте
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_data = bot_info["result"]
                print(f"✅ Бот активен:")
                print(f"   Имя: {bot_data['first_name']}")
                print(f"   Username: @{bot_data['username']}")
                print(f"   ID: {bot_data['id']}")
                print(f"   Ссылка: https://t.me/{bot_data['username']}")
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

def check_server_logs():
    """Проверяет логи сервера"""
    print("\n📋 Проверка статуса сервера...")
    
    try:
        # Проверяем health endpoint
        response = requests.get(
            "https://target-ai-prlm.onrender.com/health",
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Сервер запущен и отвечает")
            
            # Проверяем demo endpoint
            demo_response = requests.get(
                "https://target-ai-prlm.onrender.com/api/workflow/demo",
                timeout=15
            )
            
            if demo_response.status_code == 200:
                print("✅ API endpoints работают")
                return True
            else:
                print(f"⚠️  Demo endpoint недоступен: HTTP {demo_response.status_code}")
                return False
        else:
            print(f"❌ Сервер недоступен: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения с сервером: {e}")
        return False

def test_bot_interaction():
    """Тестирует взаимодействие с ботом"""
    print("\n💬 Инструкции для тестирования бота:")
    print("1. Откройте Telegram")
    print("2. Найдите бота: https://t.me/aidigitaltarget_bot")
    print("3. Нажмите 'START' или отправьте /start")
    print("4. Бот должен ответить главным меню с кнопками:")
    print("   - 📊 Мои кампании")
    print("   - 🎯 Создать кампанию")
    print("   - 📈 Аналитика")
    print("   - ⚙️ Настройки")
    print("\n5. Попробуйте загрузить изображение - бот должен его проанализировать")

def wait_for_deployment():
    """Ждет завершения деплоя"""
    print("\n⏳ Ожидание перезапуска сервиса...")
    print("Это может занять 2-5 минут...")
    
    for i in range(30):  # Ждем до 5 минут
        try:
            response = requests.get(
                "https://target-ai-prlm.onrender.com/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"\n✅ Сервис перезапущен! (через {i*10} секунд)")
                return True
        except:
            pass
        
        print(f"⏳ Попытка {i+1}/30...", end="\r")
        time.sleep(10)
    
    print("\n⚠️  Превышено время ожидания. Проверьте статус в Render.com")
    return False

if __name__ == "__main__":
    print("🔍 Проверка статуса Target AI после настройки")
    print("=" * 50)
    
    # Проверяем статус бота
    bot_ok = check_bot_status()
    
    # Проверяем сервер
    server_ok = check_server_logs()
    
    # Инструкции по тестированию
    if bot_ok and server_ok:
        test_bot_interaction()
        print("\n🎉 Всё настроено правильно!")
        print("\n📝 Что делать дальше:")
        print("1. Протестируйте бота в Telegram")
        print("2. Загрузите изображение для анализа")
        print("3. Создайте рекламную кампанию")
        print("4. Если нужна реальная интеграция с Facebook/OpenAI,")
        print("   замените тестовые ключи на настоящие")
    else:
        print("\n❌ Что-то ещё не работает:")
        if not bot_ok:
            print("   - Проверьте TELEGRAM_BOT_TOKEN в Render.com")
        if not server_ok:
            print("   - Проверьте логи в Render.com на предмет ошибок")
        print("\n💡 Возможные причины:")
        print("   - Сервис ещё перезапускается (подождите 2-3 минуты)")
        print("   - Переменные окружения неправильно настроены")
        print("   - Есть ошибки в коде (проверьте логи)")
