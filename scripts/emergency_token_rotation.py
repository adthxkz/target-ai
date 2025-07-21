#!/usr/bin/env python3
"""
🚨 КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ 🚨

Токен Telegram бота был обнаружен в публичном репозитории GitHub!
Этот скрипт поможет вам безопасно сменить токен.

НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ:
1. Создайте новый токен через @BotFather
2. Обновите переменные окружения
3. Проверьте логи на предмет несанкционированного доступа
"""

import os
import requests
import asyncio
import sys
from datetime import datetime

def print_security_warning():
    """Выводит предупреждение безопасности"""
    print("=" * 80)
    print("🚨 КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ 🚨")
    print("=" * 80)
    print("Обнаружена утечка токена Telegram бота в публичном репозитории!")
    print("GitHub Security Alert: Publicly leaked secret")
    print("Время обнаружения:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    print("СКОМПРОМЕТИРОВАННЫЙ ТОКЕН ДОЛЖЕН БЫТЬ НЕМЕДЛЕННО ЗАМЕНЕН!")
    print("=" * 80)
    print()

def get_instructions():
    """Возвращает пошаговые инструкции"""
    return """
ПОШАГОВЫЕ ИНСТРУКЦИИ ПО РОТАЦИИ ТОКЕНА:

1. 🔑 СОЗДАЙТЕ НОВЫЙ ТОКЕН:
   - Откройте Telegram
   - Найдите @BotFather
   - Отправьте /mybots
   - Выберите вашего бота
   - Нажмите "API Token"
   - Нажмите "Revoke current token" (ОБЯЗАТЕЛЬНО!)
   - Скопируйте новый токен

2. 🌐 ОБНОВИТЕ RENDER.COM:
   - Войдите в https://dashboard.render.com
   - Найдите сервис target-ai
   - Перейдите в Environment
   - Обновите TELEGRAM_BOT_TOKEN
   - Нажмите Save Changes

3. 🧪 ТЕСТИРОВАНИЕ:
   - Подождите 2-3 минуты для перезапуска
   - Запустите: python test_new_token.py
   - Проверьте бота в Telegram

4. 📊 ПРОВЕРКА ЛОГОВ:
   - Проверьте логи Render.com
   - Мониторьте активность бота
   - Убедитесь в отсутствии подозрительной активности

5. 🔒 ЗАКРОЙТЕ ALERT:
   - В GitHub перейдите в Security > Secret scanning alerts
   - Найдите alert с токеном
   - Нажмите "Close as revoked"
"""

def check_old_token_status():
    """Проверяет статус старого (скомпрометированного) токена"""
    old_token = "8137758490:AAH3bH4Rwvq5CJPxQNtn_VN-2-eKujSqW8o"
    
    print("🔍 Проверка статуса скомпрометированного токена...")
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{old_token}/getMe", timeout=10)
        if response.status_code == 200:
            print("❌ ОПАСНОСТЬ: Старый токен ВСЁ ЕЩЁ АКТИВЕН!")
            print("   НЕМЕДЛЕННО отзовите его через @BotFather!")
            return False
        else:
            print("✅ Хорошо: Старый токен неактивен или отозван")
            return True
    except Exception as e:
        print(f"⚠️ Не удалось проверить старый токен: {e}")
        return None

def check_new_token():
    """Проверяет новый токен из переменных окружения"""
    new_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not new_token:
        print("❌ Новый токен не найден в переменных окружения")
        return False
    
    if new_token == "8137758490:AAH3bH4Rwvq5CJPxQNtn_VN-2-eKujSqW8o":
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Используется скомпрометированный токен!")
        return False
    
    print(f"🔍 Проверка нового токена (***{new_token[-10:]})...")
    
    try:
        response = requests.get(f"https://api.telegram.org/bot{new_token}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Новый токен работает корректно!")
            print(f"   Бот: @{bot_info['username']} ({bot_info['first_name']})")
            return True
        else:
            print(f"❌ Новый токен не работает: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки нового токена: {e}")
        return False

def main():
    """Основная функция"""
    print_security_warning()
    
    # Проверяем статус старого токена
    old_token_revoked = check_old_token_status()
    print()
    
    # Проверяем новый токен
    new_token_works = check_new_token()
    print()
    
    # Выводим инструкции
    print(get_instructions())
    
    # Итоговый статус
    print("=" * 80)
    print("📊 ИТОГОВЫЙ СТАТУС БЕЗОПАСНОСТИ:")
    print("=" * 80)
    
    if old_token_revoked and new_token_works:
        print("✅ БЕЗОПАСНОСТЬ ВОССТАНОВЛЕНА!")
        print("   - Старый токен отозван")
        print("   - Новый токен работает")
        print("   - Можно закрыть GitHub Security Alert")
    elif old_token_revoked is False:
        print("🚨 КРИТИЧЕСКАЯ УЯЗВИМОСТЬ!")
        print("   - Старый токен ВСЁ ЕЩЁ АКТИВЕН!")
        print("   - НЕМЕДЛЕННО отзовите его через @BotFather!")
    elif not new_token_works:
        print("⚠️ НОВЫЙ ТОКЕН НЕ НАСТРОЕН!")
        print("   - Создайте новый токен")
        print("   - Обновите переменные окружения")
    else:
        print("⏳ РОТАЦИЯ В ПРОЦЕССЕ...")
        print("   - Следуйте инструкциям выше")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
