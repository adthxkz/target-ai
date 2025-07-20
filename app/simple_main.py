from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
if os.path.exists(".env"):
    load_dotenv()

# Настройки
IS_MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

# Тестовые данные
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

# Инициализация приложения
app = FastAPI(
    title="Target AI API",
    description="API для управления рекламными кампаниями в Facebook",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Target AI API v1.0.0", "status": "running"}

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
    return JSONResponse({"campaigns": MOCK_CAMPAIGNS})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
