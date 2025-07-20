import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from ..app.main import app
from ..app.services.facebook_ads import FacebookAdsService
import os
import json
from datetime import datetime

# Фикстура для клиента тестирования
@pytest.fixture
def client():
    return TestClient(app)

# Фикстура для асинхронного клиента
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Фикстура для API ключа
@pytest.fixture
def api_key():
    return {"X-API-Key": os.getenv("API_KEY", "test_key")}

# Тесты эндпоинтов
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

async def test_create_campaign(async_client, api_key):
    campaign_data = {
        "name": f"Test Campaign {datetime.now()}",
        "objective": "REACH",
        "daily_budget": 100.0,
        "status": "PAUSED"
    }
    
    response = await async_client.post(
        "/campaigns",
        json=campaign_data,
        headers=api_key
    )
    assert response.status_code == 200
    assert "campaign_id" in response.json()

async def test_list_campaigns(async_client, api_key):
    response = await async_client.get("/campaigns", headers=api_key)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_create_targeting(async_client, api_key):
    targeting_data = {
        "countries": ["US"],
        "age_min": 25,
        "age_max": 55,
        "genders": [1, 2],
        "interests": ["technology"]
    }
    
    response = await async_client.post(
        "/targeting",
        json=targeting_data,
        headers=api_key
    )
    assert response.status_code == 200
    assert "age_min" in response.json()
    assert "geo_locations" in response.json()

async def test_upload_creative(async_client, api_key):
    creative_data = {
        "image_path": "test_image.jpg",
        "name": "Test Creative"
    }
    
    response = await async_client.post(
        "/creatives",
        json=creative_data,
        headers=api_key
    )
    assert response.status_code == 200
    assert "type" in response.json()
    assert response.json()["type"] == "image"

async def test_create_ad(async_client, api_key):
    ad_data = {
        "campaign_id": "test_campaign_id",
        "creative_id": "test_creative_id",
        "creative_type": "image",
        "ad_text": "Test Ad",
        "headline": "Test Headline",
        "link": "https://example.com",
        "targeting": {
            "countries": ["US"],
            "age_min": 25,
            "age_max": 55
        }
    }
    
    response = await async_client.post(
        "/ads",
        json=ad_data,
        headers=api_key
    )
    assert response.status_code == 200
    assert "ad_id" in response.json()
    assert "adset_id" in response.json()

# Тесты обработки ошибок
async def test_invalid_api_key(async_client):
    response = await async_client.get(
        "/campaigns",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 403

async def test_invalid_campaign_data(async_client, api_key):
    campaign_data = {
        "name": "Test Campaign",
        # Пропускаем обязательные поля
    }
    
    response = await async_client.post(
        "/campaigns",
        json=campaign_data,
        headers=api_key
    )
    assert response.status_code == 422  # Validation Error

async def test_campaign_not_found(async_client, api_key):
    response = await async_client.get(
        "/campaigns/non_existent_id/stats",
        headers=api_key
    )
    assert response.status_code == 400
