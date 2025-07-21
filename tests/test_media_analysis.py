import requests
import io
from PIL import Image
import json

def test_image_analysis():
    """Тестирует анализ изображения"""
    print("🧪 Тестирование анализа изображения...")
    
    # Создаем простое тестовое изображение
    img = Image.new('RGB', (500, 300), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    # Отправляем на локальный Flask API
    try:
        response = requests.post(
            'http://localhost:5000/api/analyze-media',
            files={'file': ('test_image.jpg', img_buffer, 'image/jpeg')},
            data={'user_preferences': 'технологическая компания'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Анализ изображения успешен!")
            print(f"📊 Целевая аудитория: {result['analysis']['target_audience']['age_range']}")
            print(f"🎯 Цель кампании: {result['analysis']['campaign_objective']}")
            print(f"💰 Бюджет: {result['analysis']['budget_recommendation']['daily_budget']} {result['analysis']['budget_recommendation']['currency']}")
            print(f"📝 Предложения текста: {result['analysis']['ad_copy_suggestions'][0]}")
        else:
            print(f"❌ Ошибка: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Flask API не запущен на localhost:5000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_video_analysis():
    """Тестирует анализ видео (мок)"""
    print("\n🎥 Тестирование анализа видео...")
    
    # Создаем мок видео файл 
    video_data = b"mock_video_data"
    
    try:
        response = requests.post(
            'http://localhost:5000/api/analyze-media',
            files={'file': ('test_video.mp4', io.BytesIO(video_data), 'video/mp4')},
            data={'user_preferences': 'развлекательный контент'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Анализ видео успешен!")
            print(f"📊 Целевая аудитория: {result['analysis']['target_audience']['age_range']}")
            print(f"🎯 Цель кампании: {result['analysis']['campaign_objective']}")
            print(f"💰 Бюджет: {result['analysis']['budget_recommendation']['daily_budget']} {result['analysis']['budget_recommendation']['currency']}")
            print(f"⏱️ Длительность: {result['analysis']['creative_insights'].get('duration', 'Не указано')}")
        else:
            print(f"❌ Ошибка: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Flask API не запущен на localhost:5000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_production_api():
    """Тестирует продакшн API на Render"""
    print("\n🌐 Тестирование продакшн API...")
    
    # Создаем простое тестовое изображение
    img = Image.new('RGB', (300, 200), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    try:
        response = requests.post(
            'https://target-ai-prlm.onrender.com/api/analyze-media',
            files={'file': ('test_prod.png', img_buffer, 'image/png')},
            data={'user_preferences': 'стартап в сфере ИТ'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Продакшн API работает!")
            print(f"📊 Целевая аудитория: {result['analysis']['target_audience']['demographics']}")
            print(f"🎨 Стиль креатива: {result['analysis']['creative_insights']['style']}")
            print(f"🔧 Сервисы доступны: {result.get('services_available', 'неизвестно')}")
        else:
            print(f"❌ Ошибка продакшн API: {response.status_code}")
            try:
                print(f"Детали: {response.json()}")
            except:
                print(f"Ответ: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Ошибка продакшн API: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов анализатора медиа...")
    test_image_analysis()
    test_video_analysis()
    test_production_api()
    print("\n✨ Тестирование завершено!")
