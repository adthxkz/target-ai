import os
import asyncio
from app.services.media_analysis import MediaAnalysisService
from PIL import Image
import io
import json

async def test_real_openai_analysis():
    """Детальный тест OpenAI анализа"""
    print("🧪 Детальное тестирование OpenAI анализа...")
    
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    service = MediaAnalysisService()
    
    print(f"🔑 API ключ найден: {'Да' if service.openai_api_key else 'Нет'}")
    print(f"🤖 Клиент создан: {'Да' if service.client else 'Нет'}")
    
    # Создаем более сложное изображение для анализа
    img = Image.new('RGB', (600, 400), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Рисуем простой логотип и текст
    draw.rectangle([50, 50, 550, 150], fill='blue')
    draw.rectangle([60, 60, 540, 140], fill='white')
    
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 80), "TECH STARTUP", fill='blue', font=font)
    draw.text((100, 200), "Innovation for Everyone", fill='gray', font=font)
    draw.text((100, 300), "Join us today!", fill='green', font=font)
    
    # Сохраняем изображение
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    print("🖼️ Создано тестовое изображение с текстом 'TECH STARTUP'")
    
    try:
        print("📤 Отправляем запрос к OpenAI...")
        result = await service.analyze_image(img_buffer.read(), "tech_startup.png")
        
        print(f"📥 Получен ответ: {result['status']}")
        
        if 'raw_response' in result:
            raw = result['raw_response']
            if "режим разработки" in raw:
                print("⚠️ Это fallback ответ, не реальный OpenAI")
            else:
                print("✅ Это реальный ответ от OpenAI!")
                print(f"📄 Сырой ответ (первые 200 символов): {raw[:200]}...")
        
        analysis = result.get('analysis', {})
        print(f"\n📊 Результат анализа:")
        print(f"🎯 Цель кампании: {analysis.get('campaign_objective')}")
        print(f"👥 Возраст аудитории: {analysis.get('target_audience', {}).get('age_range')}")
        print(f"💡 Интересы: {analysis.get('target_audience', {}).get('interests', [])[:3]}")
        print(f"💰 Бюджет: ${analysis.get('budget_recommendation', {}).get('daily_budget')}")
        print(f"🎨 Стиль: {analysis.get('creative_insights', {}).get('style')}")
        
        # Проверяем, есть ли специфичные для изображения данные
        if "TECH" in str(analysis) or "startup" in str(analysis).lower():
            print("✅ Анализ учитывает содержимое изображения!")
        else:
            print("⚠️ Анализ не учитывает содержимое изображения (возможно fallback)")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_openai_analysis())
