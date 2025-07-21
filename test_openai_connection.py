import os
import asyncio
from app.services.media_analysis import MediaAnalysisService
from PIL import Image
import io

async def test_openai_directly():
    """Тестирует прямое подключение к OpenAI"""
    print("🔑 Тестирование подключения к OpenAI...")
    
    service = MediaAnalysisService()
    
    if service.client:
        print("✅ OpenAI клиент инициализирован успешно")
        
        # Создаем простое тестовое изображение
        img = Image.new('RGB', (300, 200), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        print("🖼️ Отправляем изображение на анализ в OpenAI...")
        
        try:
            result = await service.analyze_image(img_buffer.read(), "test_openai.jpg")
            
            if result['status'] == 'success':
                print("✅ OpenAI анализ успешен!")
                analysis = result['analysis']
                
                if isinstance(analysis, dict) and 'target_audience' in analysis:
                    print(f"🎯 Анализ содержит: {list(analysis.keys())}")
                    print(f"👥 Аудитория: {analysis.get('target_audience', {}).get('age_range', 'Не указано')}")
                    print(f"💡 Цель: {analysis.get('campaign_objective', 'Не указано')}")
                else:
                    print(f"⚠️ Неожиданный формат ответа: {type(analysis)}")
                    print(f"Raw response: {result.get('raw_response', '')[:200]}...")
            else:
                print(f"❌ Анализ неуспешен: {result}")
                
        except Exception as e:
            print(f"❌ Ошибка при анализе: {e}")
            
    else:
        print("❌ OpenAI клиент не инициализирован")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print(f"🔑 API ключ найден: {api_key[:10]}...")
        else:
            print("❌ OPENAI_API_KEY не найден в переменных окружения")

if __name__ == "__main__":
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(test_openai_directly())
