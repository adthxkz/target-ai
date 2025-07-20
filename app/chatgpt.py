import os
import base64
import json
from typing import Union
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие API ключа
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY не найден в переменных окружения")

def encode_image(image_path: Union[str, Path, bytes]) -> str:
    """Кодирует изображение в base64."""
    if isinstance(image_path, (str, Path)):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    elif isinstance(image_path, bytes):
        return base64.b64encode(image_path).decode('utf-8')
    else:
        raise ValueError("Неподдерживаемый тип данных изображения")

async def analyze_image(image_data: Union[str, Path, bytes]) -> dict:
    """Анализирует изображение с помощью GPT-4 Vision."""
    base64_image = encode_image(image_data)
    
    prompt = """Опиши, что изображено и придумай рекламный заголовок, описание и целевую аудиторию. 
    Ответ верни в виде JSON с полями: title, description, audience."""

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000,
        temperature=0.7
    )

    try:
        # Пытаемся распарсить JSON из ответа
        result = json.loads(response.choices[0].message.content)
        return {"response": json.dumps(result, ensure_ascii=False)}
    except (json.JSONDecodeError, AttributeError):
        # Если не удалось распарсить JSON или получить content, возвращаем исходный текст
        message_content = response.choices[0].message.content if hasattr(response.choices[0].message, 'content') else str(response.choices[0].message)
        return {"response": message_content}

async def generate_ad_text(niche: str, goal: str):
    """Генерирует рекламный текст на основе ниши и цели."""
    prompt = f"""
    Ты маркетолог. Клиент хочет запустить рекламу в нише "{niche}", с целью "{goal}".
    Придумай:
    - Заголовок
    - Описание
    - Целевую аудиторию
    """
    
    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return {"response": response.choices[0].message.content}
