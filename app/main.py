from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os
import logging
import asyncio
from dotenv import load_dotenv
from .telegram_integration import start_bot
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import json
from .db.database import init_db

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

# Загрузка переменных окружения (только для локальной разработки)
if os.path.exists(".env"):
    load_dotenv()

# Получение настроек Facebook
FB_APP_ID = os.getenv("FACEBOOK_APP_ID")
FB_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
# Динамическое определение REDIRECT_URI на основе окружения
IS_PRODUCTION = os.getenv("RENDER", "false").lower() == "true"
IS_MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"  # Временный режим разработки
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
FB_REDIRECT_URI = f"{BASE_URL}/auth/facebook/callback"
FB_SCOPE = "ads_management,ads_read"

# Тестовые данные для разработки
MOCK_CAMPAIGNS = [
    {
        "id": "123456789",
        "name": "Test Campaign 1",
        "status": "ACTIVE",
        "objective": "CONVERSIONS",
        "daily_budget": 1000,
        "lifetime_budget": 10000,
        "start_time": "2025-07-01T00:00:00+0000",
        "end_time": "2025-07-31T23:59:59+0000"
    },
    {
        "id": "987654321",
        "name": "Test Campaign 2",
        "status": "PAUSED",
        "objective": "TRAFFIC",
        "daily_budget": 500,
        "lifetime_budget": 5000,
        "start_time": "2025-07-15T00:00:00+0000",
        "end_time": "2025-08-15T23:59:59+0000"
    }
]

MOCK_AD_ACCOUNT = {
    "id": "act_123456789",
    "name": "Test Ad Account",
    "currency": "USD",
    "timezone_name": "America/Los_Angeles"
}

# Инициализация приложения
app = FastAPI(
    title="Target AI API",
    description="API для управления рекламными кампаниями в Facebook",
    version="1.0.0"
)

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
    try:
        await start_bot()
        logger.info("Телеграм бот запущен")
    except Exception as e:
        logger.error(f"Ошибка запуска телеграм бота: {e}")

# Добавляем CORS middleware
# Настройка разрешенных доменов для CORS
allowed_origins = [
    BASE_URL,
    "http://localhost:3000",  # для локальной разработки
    "https://target-ai-prlm.onrender.com",  # для продакшена
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Словарь для хранения временных данных пользователей
user_states = {}

@app.get("/auth/facebook")
async def facebook_auth():
    """Начало процесса авторизации Facebook"""
    logger.info(f"Starting Facebook auth process. REDIRECT_URI: {FB_REDIRECT_URI}")
    
    if IS_MOCK_MODE:
        logger.info("Using mock mode - redirecting to mock callback")
        return RedirectResponse(url=f"{BASE_URL}/auth/facebook/callback?code=mock_code")
        
    if not FB_APP_ID or not FB_APP_SECRET:
        logger.error("Missing Facebook credentials")
        raise HTTPException(status_code=500, detail="Facebook credentials not configured")
    
    auth_url = f"https://www.facebook.com/v17.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&scope={FB_SCOPE}"
    logger.info(f"Redirecting to Facebook auth URL: {auth_url}")
    return RedirectResponse(url=auth_url)

@app.get("/auth/facebook/callback")
async def facebook_callback(code: str = None, error: str = None):
    """Обработка callback от Facebook"""
    logger.info("Received Facebook callback")
    
    if error:
        logger.error(f"Facebook OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        logger.error("No code provided in callback")
        raise HTTPException(status_code=400, detail="No code provided")
        
    if IS_MOCK_MODE and code == "mock_code":
        logger.info("Mock mode - returning test data")
        return JSONResponse({
            "status": "success",
            "access_token": "mock_access_token_123",
            "accounts": [MOCK_AD_ACCOUNT],
            "campaigns": MOCK_CAMPAIGNS
        })
    
    # Получаем access token
    token_url = f"https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "redirect_uri": FB_REDIRECT_URI,
        "code": code
    }
    
    import requests
    response = requests.get(token_url, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    # Инициализируем Facebook API
    FacebookAdsApi.init(FB_APP_ID, FB_APP_SECRET, access_token)
    
    # Получаем список рекламных аккаунтов
    try:
        me = requests.get(f"https://graph.facebook.com/v17.0/me/adaccounts", 
                         params={"access_token": access_token})
        accounts = me.json().get("data", [])
        
        # Анализируем рекламные кампании для первого аккаунта
        if accounts:
            account = AdAccount(accounts[0]["id"])
            campaigns = account.get_campaigns(fields=["name", "status", "objective"])
            return JSONResponse({
                "status": "success",
                "access_token": access_token,
                "accounts": accounts,
                "campaigns": [campaign.export_all_data() for campaign in campaigns]
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"status": "error", "message": "No ad accounts found"})

@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    return {"message": "Test endpoint works!", "timestamp": str(datetime.now())}

@app.get("/api/campaigns")
async def get_campaigns():
    """Получение списка рекламных кампаний (тестовые данные)"""
    if not IS_MOCK_MODE:
        raise HTTPException(status_code=501, detail="Only available in mock mode")
    return JSONResponse({"campaigns": MOCK_CAMPAIGNS})

@app.get("/api/ad-account")
async def get_ad_account():
    """Получение информации о рекламном аккаунте (тестовые данные)"""
    if not IS_MOCK_MODE:
        raise HTTPException(status_code=501, detail="Only available in mock mode")
    return JSONResponse({"account": MOCK_AD_ACCOUNT})

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
