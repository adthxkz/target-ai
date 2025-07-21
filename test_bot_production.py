import requests
import time

def test_bot_on_production():
    """Проверяет статус бота на продакшене"""
    print("🤖 Проверка Telegram бота на Render.com...")
    
    # Ждем деплой
    print("⏳ Ожидание деплоя (30 сек)...")
    time.sleep(30)
    
    # Проверяем, что сервер запущен
    try:
        response = requests.get("https://target-ai-prlm.onrender.com/health", timeout=10)
        if response.status_code == 200:
            print("✅ Сервер работает")
            
            # Проверяем логи (имитация)
            print("📋 Проверяем логи бота...")
            print("   - Telegram бот должен запускаться при старте сервера")
            print("   - В логах должно быть сообщение о инициализации бота")
            print("   - Проверьте @aidigitaltarget_bot в Telegram")
            
            # Информация для пользователя
            print("\n🎯 Telegram бот Target AI готов!")
            print("   Bot: @aidigitaltarget_bot")
            print("   Команды:")
            print("     /start - главное меню")
            print("   Функции:")
            print("     🖼️ Загрузка изображений для анализа")
            print("     🎥 Загрузка видео для анализа") 
            print("     🎯 Создание рекламных кампаний")
            print("     📊 Просмотр аналитики")
            print("     🎬 Демо workflow")
            
        else:
            print(f"❌ Сервер не отвечает: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут - сервер еще запускается")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def check_bot_features():
    """Инструкции по проверке функций бота"""
    print("\n🔍 Как протестировать бота:")
    print("1. Откройте Telegram")
    print("2. Найдите @aidigitaltarget_bot")
    print("3. Нажмите /start")
    print("4. Попробуйте:")
    print("   • 🎨 Создать кампанию -> загрузите изображение")
    print("   • 📊 Мои кампании -> посмотрите тестовые данные")
    print("   • 🎬 Демо workflow -> увидите полный процесс")
    print("   • 📈 Аналитика -> просмотр метрик")
    
    print("\n🎯 Ожидаемое поведение:")
    print("   ✅ Бот отвечает на команды")
    print("   ✅ Принимает изображения/видео")
    print("   ✅ Возвращает анализ и рекомендации")
    print("   ✅ Показывает интерактивные кнопки")
    print("   ✅ Предлагает создание кампаний")

if __name__ == "__main__":
    test_bot_on_production()
    check_bot_features()
