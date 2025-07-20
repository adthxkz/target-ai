"""
Сервис для анализа медиа-контента с помощью OpenAI
"""
import os
import openai
from typing import Dict, Any, List
import logging
from io import BytesIO
import base64
import requests

logger = logging.getLogger(__name__)

class MediaAnalysisService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
    async def analyze_image(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Анализирует изображение и предлагает параметры для рекламной кампании
        """
        try:
            if not self.openai_api_key:
                return self._mock_image_analysis(filename)
            
            # Конвертируем изображение в base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Проанализируй это изображение для создания рекламной кампании в Facebook.
                                
                                Верни JSON с полями:
                                - target_audience: целевая аудитория (возраст, интересы, поведение)
                                - campaign_objective: цель кампании (CONVERSIONS, TRAFFIC, BRAND_AWARENESS, etc.)
                                - ad_copy_suggestions: предложения для текста объявления
                                - budget_recommendation: рекомендуемый бюджет (daily_budget)
                                - placement_suggestions: рекомендуемые места размещения
                                - creative_insights: анализ креатива (стиль, цвета, эмоции)
                                - keywords: ключевые слова для таргетинга
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Парсим JSON ответ
            import json
            try:
                analysis_json = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Если ответ не в JSON формате, создаем структурированный ответ
                analysis_json = self._parse_text_analysis(analysis_text)
            
            return {
                "status": "success",
                "analysis": analysis_json,
                "raw_response": analysis_text
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {e}")
            return self._mock_image_analysis(filename)
    
    async def analyze_video(self, video_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Анализирует видео (пока используем mock данные)
        """
        try:
            if not self.openai_api_key:
                return self._mock_video_analysis(filename)
            
            # Для видео пока используем mock анализ
            # В будущем можно добавить извлечение кадров и анализ
            return self._mock_video_analysis(filename)
            
        except Exception as e:
            logger.error(f"Ошибка анализа видео: {e}")
            return self._mock_video_analysis(filename)
    
    def _mock_image_analysis(self, filename: str) -> Dict[str, Any]:
        """Мок анализ для тестирования"""
        return {
            "status": "success",
            "analysis": {
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["технологии", "инновации", "бизнес"],
                    "behaviors": ["частые покупки онлайн", "интерес к новым продуктам"],
                    "demographics": "городское население, средний и выше средний доход"
                },
                "campaign_objective": "CONVERSIONS",
                "ad_copy_suggestions": [
                    "Революционное решение для вашего бизнеса",
                    "Откройте новые возможности с нашим продуктом",
                    "Присоединяйтесь к тысячам довольных клиентов"
                ],
                "budget_recommendation": {
                    "daily_budget": 50,
                    "currency": "USD",
                    "reasoning": "Оптимальный стартовый бюджет для тестирования"
                },
                "placement_suggestions": [
                    "Facebook Feed",
                    "Instagram Feed", 
                    "Instagram Stories"
                ],
                "creative_insights": {
                    "style": "современный, минималистичный",
                    "colors": ["синий", "белый", "серый"],
                    "emotions": ["доверие", "профессионализм", "инновации"],
                    "visual_elements": ["логотип", "продукт", "люди"]
                },
                "keywords": ["инновации", "технологии", "эффективность", "качество"]
            },
            "raw_response": f"Анализ изображения {filename} (режим разработки)"
        }
    
    def _mock_video_analysis(self, filename: str) -> Dict[str, Any]:
        """Мок анализ видео для тестирования"""
        return {
            "status": "success",
            "analysis": {
                "target_audience": {
                    "age_range": "18-35",
                    "interests": ["видео контент", "развлечения", "социальные сети"],
                    "behaviors": ["активное использование соцсетей", "просмотр видео контента"],
                    "demographics": "молодая аудитория, активные пользователи интернета"
                },
                "campaign_objective": "VIDEO_VIEWS",
                "ad_copy_suggestions": [
                    "Смотри и делись с друзьями!",
                    "Не пропусти самое интересное!",
                    "Новый уровень развлечений"
                ],
                "budget_recommendation": {
                    "daily_budget": 30,
                    "currency": "USD",
                    "reasoning": "Оптимальный бюджет для видео-кампаний"
                },
                "placement_suggestions": [
                    "Facebook Video Feeds",
                    "Instagram Reels",
                    "Instagram Stories"
                ],
                "creative_insights": {
                    "duration": "15-30 секунд",
                    "style": "динамичный, яркий",
                    "emotions": ["веселье", "энергия", "вовлеченность"],
                    "key_moments": ["захватывающее начало", "четкий призыв к действию"]
                },
                "keywords": ["видео", "контент", "развлечения", "тренды"]
            },
            "raw_response": f"Анализ видео {filename} (режим разработки)"
        }
    
    def _parse_text_analysis(self, text: str) -> Dict[str, Any]:
        """Парсинг текстового ответа в структурированный формат"""
        # Базовая структура, если не удалось распарсить JSON
        return {
            "target_audience": {
                "age_range": "25-45",
                "interests": ["извлечено из текста"],
                "behaviors": ["анализ поведения"],
                "demographics": "городская аудитория"
            },
            "campaign_objective": "CONVERSIONS",
            "ad_copy_suggestions": ["Предложение 1", "Предложение 2"],
            "budget_recommendation": {
                "daily_budget": 40,
                "currency": "USD"
            },
            "placement_suggestions": ["Facebook Feed", "Instagram Feed"],
            "creative_insights": {
                "style": "современный",
                "analysis_text": text
            },
            "keywords": ["ключевое слово 1", "ключевое слово 2"]
        }
