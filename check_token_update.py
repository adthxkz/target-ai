#!/usr/bin/env python3
"""
Проверка статуса после обновления токена в Render.com
"""

import requests
import time

def check_webhook_with_new_token():
    """Проверяет webhook с новым токеном"""
    # Загружаем токен из переменных окружения
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    new_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not new_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return False
    
    print("🔗 Проверка webhook с новым токеном...")
    print(f"Токен: {new_token[:15]}...")
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{new_token}/getWebhookInfo",
            timeout=10
        )
        
        if response.status_code == 200:
            webhook_info = response.json()
            if webhook_info.get("ok"):
                result = webhook_info["result"]
                webhook_url = result.get("url", "")
                
                print(f"Webhook URL: {webhook_url}")
                print(f"Последняя ошибка: {result.get('last_error_message', 'нет')}")
                print(f"Ожидающих обновлений: {result.get('pending_update_count', 0)}")
                
                if webhook_url == "https://target-ai-prlm.onrender.com/webhook/telegram":
                    print("✅ Webhook установлен корректно")
                    return True
                elif webhook_url:
                    print(f"⚠️ Webhook установлен, но неправильный URL: {webhook_url}")
                    return False
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

def wait_for_service_restart():
    """Ждет перезапуска сервиса"""
    print("⏳ Ожидание перезапуска сервиса Render.com...")
    
    for i in range(20):  # Ждем до 10 минут
        try:
            response = requests.get(
                "https://target-ai-prlm.onrender.com/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"\n✅ Сервис перезапущен! (через {i*30} секунд)")
                return True
        except:
            pass
        
        print(f"⏳ Попытка {i+1}/20... (подождите перезапуска)", end="\r")
        time.sleep(30)
    
    print("\n⚠️ Превышено время ожидания")
    return False

def test_bot_response():
    """Тестирует ответ бота"""
    print("\n🤖 Инструкции для тестирования:")
    print("1. Откройте: https://t.me/aidigitaltarget_bot")
    print("2. Отправьте /start")
    print("3. Бот должен ответить главным меню с кнопками")
    print("4. Попробуйте загрузить изображение")

if __name__ == "__main__":
    print("🔄 Проверка обновления токена")
    print("=" * 40)
    
    # Ждем перезапуска
    service_ok = wait_for_service_restart()
    
    if service_ok:
        # Проверяем webhook
        webhook_ok = check_webhook_with_new_token()
        
        # Инструкции по тестированию
        test_bot_response()
        
        print("\n" + "=" * 40)
        print("📊 СТАТУС:")
        print(f"   Сервис: {'✅' if service_ok else '❌'}")
        print(f"   Webhook: {'✅' if webhook_ok else '❌'}")
        
        if service_ok and webhook_ok:
            print("\n🎉 Обновление токена завершено!")
            print("   Бот готов к работе")
        else:
            print("\n⚠️ Требуется дополнительная настройка")
            if not webhook_ok:
                print("   - Webhook не установлен автоматически")
                print("   - Проверьте переменные окружения в Render.com")
    else:
        print("\n❌ Сервис не перезапустился")
        print("   Проверьте логи в Render.com")
