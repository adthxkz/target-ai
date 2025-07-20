from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import json

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
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
FB_REDIRECT_URI = f"{BASE_URL}/auth/facebook/callback"
FB_SCOPE = "ads_management,ads_read"

# Инициализация приложения
app = FastAPI(
    title="Target AI API",
    description="API для управления рекламными кампаниями в Facebook",
    version="1.0.0"
)

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
