from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import asyncio
import json

from .config import settings
from .telegram_integration import start_bot, stop_bot
from .db.database import init_db
from .routers import facebook, telegram, ai_services

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(
    title="Target AI API",
    description="API для управления рекламными кампаниями в Facebook и анализа медиа",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Подключение роутеров
app.include_router(facebook.router)
app.include_router(telegram.router)
app.include_router(ai_services.router)

@app.on_event("startup")
async def startup_event():
    """Инициализация приложения"""
    try:
        await init_db()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
    
    asyncio.create_task(start_bot())

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка приложения"""
    await stop_bot()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.RENDER_EXTERNAL_URL,
        "http://localhost:3000",
        "https://target-ai-prlm.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Корневой эндпоинт API"""
    return {
        "message": "Добро пожаловать в Target AI API",
        "version": app.version,
        "status": "active",
        "docs": app.docs_url,
        "redoc": app.redoc_url
    }

@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

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
        <p><strong>Последнее обновление:</strong> 22 июля 2025 г.</p>
        <p>Мы серьезно относимся к вашей конфиденциальности. Наш сервис собирает и использует данные исключительно для функционирования и улучшения ваших рекламных кампаний.</p>
        <h2>Сбор и использование данных</h2>
        <p>Мы собираем данные, которые вы предоставляете, включая токены доступа к Facebook, для управления вашими рекламными аккаунтами. Эти данные используются только для выполнения запрошенных вами операций.</p>
        <h2>Безопасность</h2>
        <p>Мы принимаем меры для защиты вашей информации, но не можем гарантировать абсолютную безопасность.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
