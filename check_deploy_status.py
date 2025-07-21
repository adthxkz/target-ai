#!/usr/bin/env python3
"""
Проверка статуса после деплоя исправлений
"""

import requests
import time
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def wait_for_deployment():
    """Ждет завершения деплоя"""
    print("⏳ Ожидание завершения деплоя...")
    print("Проверяем каждые 30 секунд...")
    
    for i in range(10):  # Ждем до 5 минут
        try:
            response = requests.get(
                "https://target-ai-prlm.onrender.com/health",
                timeout=10
            )
            if response.status_code == 200:
                print(f"\n✅ Сервис доступен! (через {i*30} секунд)")
                return True
        except:
            pass
        
        print(f"⏳ Попытка {i+1}/10...", end="\r")
        time.sleep(30)
    
    print("\n⚠️  Превышено время ожидания")
    return False

def check_telegram_webhook():
    """Проверяет webhook telegram бота"""
    print("\n🤖 Проверка Telegram webhook...")
    
    # ВНИМАНИЕ: Используйте реальный токен из переменных окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return False
    
    try:
        # Получаем информацию о webhook
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getWebhookInfo",
            timeout=10
        )
        
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info.get("ok"):
                result = webhook_info["result"]
                webhook_url = result.get("url", "")
                
                if webhook_url:
                    print(f"✅ Webhook установлен: {webhook_url}")
                    print(f"   Последняя ошибка: {result.get('last_error_message', 'нет')}")
                    print(f"   Ожидающих обновлений: {result.get('pending_update_count', 0)}")
                    return True
                else:
                    print("❌ Webhook не установлен")
                    return False
            else:
                print(f"❌ Ошибка API: {webhook_info}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_webhook_endpoint():
    """Тестирует webhook endpoint"""
    print("\n🔗 Проверка webhook endpoint...")
    
    try:
        # Пробуем POST к webhook endpoint
        response = requests.post(
            "https://target-ai-prlm.onrender.com/webhook/telegram",
            json={"test": "ping"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook endpoint отвечает: {data}")
            return True
        else:
            print(f"❌ Webhook endpoint недоступен: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Проверка деплоя исправлений Telegram bot")
    print("=" * 50)
    
    # Ждем завершения деплоя
    deploy_ok = wait_for_deployment()
    
    if deploy_ok:
        # Проверяем webhook
        webhook_ok = check_telegram_webhook()
        
        # Проверяем endpoint
        endpoint_ok = test_webhook_endpoint()
        
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТ ПРОВЕРКИ:")
        print(f"   Деплой: {'✅' if deploy_ok else '❌'}")
        print(f"   Webhook: {'✅' if webhook_ok else '❌'}")
        print(f"   Endpoint: {'✅' if endpoint_ok else '❌'}")
        
        if deploy_ok and webhook_ok and endpoint_ok:
            print("\n🎉 Telegram bot должен работать!")
            print("\n📱 Протестируйте бота:")
            print("   https://t.me/aidigitaltarget_bot")
            print("   Отправьте /start")
        else:
            print("\n⚠️  Требуется дополнительная настройка")
            if not webhook_ok:
                print("   - Webhook не установлен автоматически")
                print("   - Возможно нужно установить переменные окружения")
    else:
        print("\n❌ Деплой не завершился или сервис недоступен")
