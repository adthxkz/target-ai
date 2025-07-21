import requests
import io
from PIL import Image, ImageDraw, ImageFont
import time

def test_production_after_deploy():
    """Тестирует продакшн API после деплоя с AI"""
    print("🌐 Ожидание деплоя и тестирование продакшн API...")
    
    # Ждем немного для завершения деплоя
    print("⏳ Ожидание 30 секунд для завершения деплоя...")
    time.sleep(30)
    
    # Создаем изображения разных типов
    test_cases = [
        {
            "name": "tech_startup",
            "color": "blue",
            "text": "AI STARTUP",
            "subtitle": "Future is now!",
            "preference": "технологический стартап с ИИ"
        },
        {
            "name": "food_delivery",
            "color": "orange",
            "text": "FAST FOOD",
            "subtitle": "Delivery 24/7",
            "preference": "служба доставки еды"
        },
        {
            "name": "fitness_app",
            "color": "green",
            "text": "GET FIT",
            "subtitle": "Your health app",
            "preference": "фитнес приложение для молодежи"
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Тестирование: {case['name']}")
        
        # Создаем изображение
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Цветной фон
        color_map = {
            "blue": "#1E40AF",
            "orange": "#F97316", 
            "green": "#16A34A"
        }
        draw.rectangle([50, 50, 550, 350], fill=color_map[case['color']])
        draw.rectangle([60, 60, 540, 340], fill='white')
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Текст
        draw.text((100, 120), case['text'], fill=color_map[case['color']], font=font_large)
        draw.text((100, 200), case['subtitle'], fill='gray', font=font_small)
        
        # Сохраняем в буфер
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        try:
            response = requests.post(
                'https://target-ai-prlm.onrender.com/api/analyze-media',
                files={'file': (f'{case["name"]}.png', img_buffer, 'image/png')},
                data={'user_preferences': case['preference']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['analysis']
                
                print(f"✅ Анализ {case['name']} успешен!")
                print(f"🎯 Цель: {analysis.get('campaign_objective', 'N/A')}")
                print(f"👥 Аудитория: {analysis.get('target_audience', {}).get('age_range', 'N/A')}")
                print(f"💡 Интересы: {', '.join(analysis.get('target_audience', {}).get('interests', [])[:3])}")
                print(f"💰 Бюджет: ${analysis.get('budget_recommendation', {}).get('daily_budget', 'N/A')}")
                print(f"🔧 AI активен: {'Да' if result.get('services_available') else 'Нет (fallback)'}")
                
                # Проверяем релевантность анализа
                content_words = case['text'].lower().split() + case['subtitle'].lower().split()
                analysis_text = str(analysis).lower()
                
                relevant_found = any(word in analysis_text for word in content_words if len(word) > 3)
                if relevant_found:
                    print("✅ Анализ учитывает содержимое!")
                else:
                    print("⚠️ Возможно, используется fallback")
                    
            else:
                print(f"❌ Ошибка {case['name']}: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Таймаут для {case['name']} - сервер еще разворачивается")
        except Exception as e:
            print(f"❌ Ошибка {case['name']}: {e}")

def test_video_analysis_prod():
    """Тестирует анализ видео на продакшене"""
    print(f"\n🎥 Тестирование анализа видео на продакшене...")
    
    # Создаем мок видео файл
    video_content = b"FAKE_VIDEO_DATA_FOR_TESTING_PRODUCTION"
    
    try:
        response = requests.post(
            'https://target-ai-prlm.onrender.com/api/analyze-media',
            files={'file': ('marketing_video.mp4', io.BytesIO(video_content), 'video/mp4')},
            data={'user_preferences': 'маркетинговое видео для SaaS продукта'},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['analysis']
            
            print(f"✅ Анализ видео успешен!")
            print(f"🎯 Цель: {analysis.get('campaign_objective', 'N/A')}")
            print(f"👥 Аудитория: {analysis.get('target_audience', {}).get('age_range', 'N/A')}")
            print(f"📱 Размещение: {', '.join(analysis.get('placement_suggestions', [])[:2])}")
            print(f"⏱️ Длительность: {analysis.get('creative_insights', {}).get('duration', 'N/A')}")
            
        else:
            print(f"❌ Ошибка видео: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка видео: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование продакшн API после деплоя с AI...")
    test_production_after_deploy()
    test_video_analysis_prod()
    print("\n✨ Тестирование завершено!")
