from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import logging
import asyncio
import httpx
import json

from .config import settings
from .telegram_integration import start_bot, stop_bot, process_telegram_update
from .db.database import init_db
from .routers import facebook

# Попытка импорта новых сервисов с обработкой ошибок
try:
    from .services.media_analysis import MediaAnalysisService
    from .services.campaign_automation import CampaignAutomationService
    SERVICES_AVAILABLE = True
    print("Новые сервисы успешно импортированы")
except ImportError as e:
    print(f"Ошибка импорта сервисов: {e}")
    SERVICES_AVAILABLE = False

from typing import Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(
    title="Target AI API",
    description="API для управления рекламными кампаниями в Facebook",
    version="1.0.0"
)

# Подключение роутеров
app.include_router(facebook.router)

# Инициализация сервисов только если они доступны
if SERVICES_AVAILABLE:
    try:
        media_analysis_service = MediaAnalysisService()
        campaign_automation_service = CampaignAutomationService()
        logger.info("Сервисы инициализированы")
    except Exception as e:
        logger.error(f"Ошибка инициализации сервисов: {e}")
        SERVICES_AVAILABLE = False

@app.on_event("startup")
async def startup_event():
    """Инициализация приложения"""
    # Инициализация базы данных
    try:
        await init_db()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
    
    # Запуск телеграм-бота
    asyncio.create_task(start_bot())

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка приложения"""
    await stop_bot()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.BASE_URL,
        "http://localhost:3000",
        "https://target-ai-prlm.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Словарь для хранения временных данных пользователей
user_states = {}

@app.get("/")
async def root():
    """Корневой эндпоинт API"""
    return {
        "message": "Добро пожаловать в Target AI API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Facebook Ads автоматизация",
            "AI анализ медиа контента",
            "Telegram бот интеграция",
            "Создание и оптимизация кампаний"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/facebook/auth",
            "campaigns": "/api/facebook/campaigns",
            "analyze": "/api/analyze-media",
            "workflow": "/api/workflow/demo"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Webhook для обработки сообщений от Telegram"""
    if not settings.RENDER:
        logger.warning("Вебхук получен в режиме разработки, игнорируется.")
        return {"status": "ignored_in_dev"}
        
    try:
        update_data = await request.json()
        await process_telegram_update(update_data)
        return {"status": "ok"}
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON от Telegram.")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Ошибка обработки telegram webhook: {e}", exc_info=True)
        # Возвращаем 200, чтобы Telegram не повторял отправку
        return {"status": "error", "message": "Internal server error"}

@app.post("/api/analyze-media")
async def analyze_media(
    file: UploadFile = File(...),
    user_preferences: Optional[str] = Form(None)
):
    """
    Анализирует загруженный медиа-файл (изображение или видео) 
    и предлагает параметры для рекламной кампании
    """
    if not SERVICES_AVAILABLE:
        # Fallback к простому мок-анализу
        return JSONResponse({
            "status": "success",
            "analysis": {
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["технологии", "маркетинг", "бизнес"],
                    "demographics": "профессионалы, городская аудитория"
                },
                "campaign_objective": "CONVERSIONS",
                "ad_copy_suggestions": [
                    "Инновационное решение для вашего бизнеса!",
                    "Увеличьте эффективность уже сегодня",
                    "Доверьтесь экспертам в своей области"
                ],
                "budget_recommendation": {
                    "daily_budget": 75,
                    "currency": "USD"
                },
                "creative_insights": {
                    "style": "профессиональный, современный",
                    "colors": ["синий", "белый", "серый"],
                    "emotions": ["доверие", "уверенность", "профессионализм"]
                }
            },
            "file_info": {
                "filename": file.filename,
                "analyzed_at": datetime.now().isoformat()
            },
            "services_available": False
        })
    
    try:
        # Проверяем тип файла
        allowed_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'video': ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime']
        }
        
        file_type = None
        for media_type, mime_types in allowed_types.items():
            if file.content_type in mime_types:
                file_type = media_type
                break
        
        if not file_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый тип файла: {file.content_type}"
            )
        
        # Проверяем размер файла (макс 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10MB)")
        
        # Анализируем медиа
        if file_type == 'image':
            analysis_result = await media_analysis_service.analyze_image(
                file_content, file.filename
            )
        else:  # video
            analysis_result = await media_analysis_service.analyze_video(
                file_content, file.filename
            )
        
        # Добавляем информацию о файле
        analysis_result["file_info"] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(file_content),
            "media_type": file_type
        }
        
        return JSONResponse(analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка анализа медиа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа файла: {str(e)}")

@app.post("/api/create-campaign")
async def create_campaign_from_analysis(request: Request):
    """
    Создает рекламную кампанию на основе результатов анализа медиа
    """
    try:
        data = await request.json()
        
        # Проверяем обязательные поля
        if "analysis_data" not in data:
            raise HTTPException(status_code=400, detail="Отсутствуют данные анализа")
        
        analysis_data = data["analysis_data"]
        user_preferences = data.get("user_preferences", {})
        
        # Создаем кампанию
        campaign_result = await campaign_automation_service.create_campaign_from_analysis(
            analysis_data, user_preferences
        )
        
        return JSONResponse(campaign_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания кампании: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания кампании: {str(e)}")

@app.get("/api/campaign/{campaign_id}/performance")
async def get_campaign_performance(campaign_id: str):
    """
    Получает метрики производительности кампании
    """
    try:
        performance = await campaign_automation_service.get_campaign_performance(campaign_id)
        return JSONResponse(performance)
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик кампании {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения метрик: {str(e)}")

@app.post("/api/campaign/{campaign_id}/optimize")
async def optimize_campaign(campaign_id: str):
    """
    Запускает оптимизацию кампании на основе текущих метрик
    """
    try:
        optimization_result = await campaign_automation_service.optimize_campaign(campaign_id)
        return JSONResponse(optimization_result)
        
    except Exception as e:
        logger.error(f"Ошибка оптимизации кампании {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка оптимизации: {str(e)}")

@app.get("/api/workflow/demo")
async def demo_full_workflow():
    """
    Демонстрирует полный рабочий процесс: анализ -> создание -> оптимизация
    """
    try:
        if not SERVICES_AVAILABLE:
            # Fallback к базовой демонстрации без сервисов
            import random
            
            # 1. Мок анализ
            mock_analysis = {
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
                "raw_response": "Анализ demo.jpg (режим разработки)"
            }
            
            # 2. Создание кампании
            campaign_id = f"camp_{random.randint(100000, 999999)}"
            campaign_result = {
                "status": "success",
                "message": "Кампания создана успешно (режим разработки)",
                "campaign": {
                    "campaign_id": campaign_id,
                    "name": f"AI Generated Campaign - {datetime.now().strftime('%Y%m%d_%H%M')}",
                    "status": "ACTIVE",
                    "objective": "CONVERSIONS",
                    "budget": 100,
                    "target_audience": mock_analysis["analysis"]["target_audience"],
                    "placements": mock_analysis["analysis"]["placement_suggestions"],
                    "ad_creative": {
                        "ad_copy": mock_analysis["analysis"]["ad_copy_suggestions"][0],
                        "keywords": mock_analysis["analysis"]["keywords"],
                        "creative_insights": mock_analysis["analysis"]["creative_insights"]
                    },
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            # 3. Метрики производительности
            performance = {
                "status": "success",
                "campaign_id": campaign_id,
                "daily_metrics": [
                    {
                        "date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                        "impressions": random.randint(100, 1000),
                        "clicks": random.randint(10, 100),
                        "conversions": random.randint(1, 10),
                        "spend": round(random.uniform(10, 100), 2)
                    } for i in range(7)
                ],
                "total_metrics": {
                    "total_impressions": random.randint(1000, 5000),
                    "total_clicks": random.randint(50, 200),
                    "total_conversions": random.randint(5, 25),
                    "total_spend": round(random.uniform(40, 80), 2),
                    "ctr": round(random.uniform(2.0, 5.0), 2),
                    "cost_per_click": round(random.uniform(0.8, 2.5), 2),
                    "cost_per_conversion": round(random.uniform(15, 40), 2),
                    "conversion_rate": round(random.uniform(3.0, 8.0), 2)
                },
                "period": "last_7_days",
                "updated_at": datetime.now().isoformat()
            }
            
            # 4. Оптимизация
            optimizations = []
            if performance["total_metrics"]["ctr"] < 3.0:
                optimizations.append({
                    "type": "creative_optimization",
                    "message": "CTR можно улучшить, обновив креатив",
                    "action": "update_creative",
                    "priority": "medium"
                })
            
            if performance["total_metrics"]["cost_per_conversion"] > 30:
                optimizations.append({
                    "type": "targeting_optimization", 
                    "message": "Рекомендуется сузить целевую аудиторию",
                    "action": "refine_targeting",
                    "priority": "high"
                })
            
            optimization_result = {
                "status": "success",
                "campaign_id": campaign_id,
                "metrics": performance["total_metrics"],
                "optimizations": optimizations,
                "analyzed_at": datetime.now().isoformat()
            }
            
            return JSONResponse({
                "status": "success",
                "workflow": {
                    "step_1_analysis": mock_analysis,
                    "step_2_campaign_creation": campaign_result,
                    "step_3_performance": performance,
                    "step_4_optimization": optimization_result
                },
                "message": "Демонстрация полного рабочего процесса завершена (fallback режим)",
                "services_available": False
            })
        
        # Используем полные сервисы если доступны
        # 1. Имитируем анализ изображения
        mock_analysis = await media_analysis_service.analyze_image(b"mock_image_data", "demo.jpg")
        
        # 2. Создаем кампанию на основе анализа
        campaign_result = await campaign_automation_service.create_campaign_from_analysis(
            mock_analysis, {"budget": 100, "campaign_name": "Demo Campaign"}
        )
        
        if campaign_result["status"] == "success":
            campaign_id = campaign_result["campaign"]["campaign_id"]
            
            # 3. Получаем метрики
            performance = await campaign_automation_service.get_campaign_performance(campaign_id)
            
            # 4. Запускаем оптимизацию
            optimization = await campaign_automation_service.optimize_campaign(campaign_id)
            
            return JSONResponse({
                "status": "success",
                "workflow": {
                    "step_1_analysis": mock_analysis,
                    "step_2_campaign_creation": campaign_result,
                    "step_3_performance": performance,
                    "step_4_optimization": optimization
                },
                "message": "Демонстрация полного рабочего процесса завершена",
                "services_available": True
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": "Ошибка создания кампании",
                "details": campaign_result
            })
        
    except Exception as e:
        logger.error(f"Ошибка демонстрации workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка демонстрации: {str(e)}")

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    """Страница с политикой конфиденциальности"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Политика конфиденциальности - Target AI</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            h2 { color: #666; }
        </style>
    </head>
    <body>
        <h1>Политика конфиденциальности Target AI</h1>
        
        <p><strong>Последнее обновление:</strong> 20 июля 2025 г.</p>
        
        <h2>1. Сбор информации</h2>
        <p>Мы собираем следующую информацию при использовании нашего сервиса:</p>
        <ul>
            <li>Данные вашего рекламного аккаунта Facebook</li>
            <li>Информацию о рекламных кампаниях</li>
            <li>Статистику и метрики рекламных объявлений</li>
        </ul>

        <h2>2. Использование информации</h2>
        <p>Собранная информация используется для:</p>
        <ul>
            <li>Оптимизации ваших рекламных кампаний</li>
            <li>Предоставления аналитики и отчетов</li>
            <li>Улучшения качества нашего сервиса</li>
        </ul>

        <h2>3. Защита информации</h2>
        <p>Мы применяем современные методы защиты для обеспечения безопасности ваших данных. Вся информация передается по защищенным каналам связи.</p>

        <h2>4. Доступ к данным</h2>
        <p>Доступ к данным имеют только авторизованные сотрудники. Мы не передаем ваши данные третьим лицам без вашего согласия.</p>

        <h2>5. Контакты</h2>
        <p>По всем вопросам, связанным с обработкой данных, обращайтесь по адресу: support@target-ai.com</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
