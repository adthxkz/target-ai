import requests
import io
from PIL import Image, ImageDraw, ImageFont
import json

def create_business_image():
    """Создает изображение в бизнес стиле"""
    img = Image.new('RGB', (800, 600), color='#1E3A8A')  # Синий
    draw = ImageDraw.Draw(img)
    
    # Добавляем простой текст
    try:
        # Пытаемся использовать системный шрифт
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # Белый прямоугольник для текста
    draw.rectangle([100, 200, 700, 400], fill='white')
    draw.text((120, 250), "BUSINESS", fill='#1E3A8A', font=font)
    draw.text((120, 310), "SOLUTION", fill='#1E3A8A', font=font)
    
    return img

def create_tech_image():
    """Создает изображение в техно стиле"""
    img = Image.new('RGB', (600, 400), color='#000000')  # Черный
    draw = ImageDraw.Draw(img)
    
    # Зеленые линии (как код)
    for i in range(0, 600, 20):
        draw.line([(i, 0), (i, 400)], fill='#00FF00', width=1)
    
    # Центральный круг
    draw.ellipse([200, 150, 400, 250], fill='#00FF41')
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((250, 190), "TECH", fill='black', font=font)
    
    return img

def create_food_image():
    """Создает изображение в пищевой тематике"""
    img = Image.new('RGB', (500, 500), color='#FFA500')  # Оранжевый
    draw = ImageDraw.Draw(img)
    
    # Круг как тарелка
    draw.ellipse([50, 50, 450, 450], fill='#FFFFFF')
    draw.ellipse([60, 60, 440, 440], fill='#FFD700')
    
    # "Еда" в центре
    draw.ellipse([200, 200, 300, 300], fill='#FF6347')  # Томатный
    
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    draw.text((210, 360), "FOOD", fill='#8B4513', font=font)
    
    return img

def test_different_images():
    """Тестирует анализ разных типов изображений"""
    print("🎨 Тестирование анализа разных типов изображений...")
    
    images = [
        ("business", create_business_image(), "корпоративная презентация"),
        ("tech", create_tech_image(), "IT стартап"),
        ("food", create_food_image(), "ресторан и доставка еды")
    ]
    
    for name, img, preference in images:
        print(f"\n📸 Тестирование {name} изображения...")
        
        # Сохраняем в буфер
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        try:
            # Тестируем на продакшене
            response = requests.post(
                'https://target-ai-prlm.onrender.com/api/analyze-media',
                files={'file': (f'{name}_test.png', img_buffer, 'image/png')},
                data={'user_preferences': preference}
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['analysis']
                
                print(f"✅ Анализ {name} успешен!")
                print(f"🎯 Цель: {analysis['campaign_objective']}")
                print(f"👥 Аудитория: {analysis['target_audience']['age_range']}")
                print(f"💡 Интересы: {', '.join(analysis['target_audience']['interests'][:3])}")
                print(f"💰 Бюджет: ${analysis['budget_recommendation']['daily_budget']}/день")
                print(f"📝 Текст: {analysis['ad_copy_suggestions'][0]}")
                print(f"🎨 Стиль: {analysis['creative_insights']['style']}")
                print(f"🔧 AI доступен: {'Да' if result.get('services_available') else 'Нет (fallback)'}")
                
            else:
                print(f"❌ Ошибка {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка {name}: {e}")

def test_video_mock():
    """Тестирует анализ видео"""
    print(f"\n🎥 Тестирование анализа видео...")
    
    # Создаем мок видео файл
    video_content = b"FAKE_VIDEO_CONTENT_FOR_TESTING"
    
    try:
        response = requests.post(
            'https://target-ai-prlm.onrender.com/api/analyze-media',
            files={'file': ('promo_video.mp4', io.BytesIO(video_content), 'video/mp4')},
            data={'user_preferences': 'промо ролик для мобильного приложения'}
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['analysis']
            
            print(f"✅ Анализ видео успешен!")
            print(f"🎯 Цель: {analysis['campaign_objective']}")
            print(f"👥 Аудитория: {analysis['target_audience']['age_range']}")
            print(f"⏱️ Длительность: {analysis['creative_insights'].get('duration', 'Не указано')}")
            print(f"📱 Размещение: {', '.join(analysis['placement_suggestions'][:2])}")
            print(f"💰 Бюджет: ${analysis['budget_recommendation']['daily_budget']}/день")
            print(f"🎭 Эмоции: {', '.join(analysis['creative_insights']['emotions'][:2])}")
            
        else:
            print(f"❌ Ошибка видео: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка видео: {e}")

if __name__ == "__main__":
    print("🚀 Расширенное тестирование анализатора медиа...")
    test_different_images()
    test_video_mock()
    print("\n✨ Все тесты завершены!")
