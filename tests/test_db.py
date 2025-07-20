import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.db.models import Base, User, Campaign, Creative
from app.db.init_db import init_db
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Используем тестовую базу данных
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def async_session():
    """Create a fresh database session for each test."""
    session_maker = await init_db()
    async with session_maker() as session:
        yield session
        # Откатываем изменения после каждого теста
        await session.rollback()

@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    # Создаем тестового пользователя
    user = User(
        telegram_id=123456789,
        fb_access_token="test_token",
        fb_account_id="test_account"
    )
    
    async_session.add(user)
    await async_session.commit()
    
    # Проверяем, что пользователь создан
    result = await async_session.get(User, user.id)
    assert result is not None
    assert result.telegram_id == 123456789
    assert result.fb_access_token == "test_token"

@pytest.mark.asyncio
async def test_create_campaign(async_session: AsyncSession):
    # Создаем тестового пользователя
    user = User(
        telegram_id=123456790,
        fb_access_token="test_token_2",
        fb_account_id="test_account_2"
    )
    async_session.add(user)
    await async_session.commit()
    
    # Создаем тестовую кампанию
    campaign = Campaign(
        fb_campaign_id="test_campaign_123",
        user_id=user.id,
        name="Test Campaign",
        status="ACTIVE",
        objective="CONVERSIONS",
        daily_budget=100.0
    )
    
    async_session.add(campaign)
    await async_session.commit()
    
    # Проверяем, что кампания создана и связана с пользователем
    result = await async_session.get(Campaign, campaign.id)
    assert result is not None
    assert result.name == "Test Campaign"
    assert result.user_id == user.id

@pytest.mark.asyncio
async def test_create_creative(async_session: AsyncSession):
    # Создаем тестового пользователя и кампанию
    user = User(
        telegram_id=123456791,
        fb_access_token="test_token_3",
        fb_account_id="test_account_3"
    )
    async_session.add(user)
    await async_session.commit()
    
    campaign = Campaign(
        fb_campaign_id="test_campaign_456",
        user_id=user.id,
        name="Test Campaign 2",
        status="ACTIVE",
        objective="CONVERSIONS",
        daily_budget=200.0
    )
    async_session.add(campaign)
    await async_session.commit()
    
    # Создаем тестовый креатив
    creative = Creative(
        campaign_id=campaign.id,
        fb_creative_id="test_creative_123",
        type="image",
        file_path="/path/to/test/image.jpg",
        analysis={"score": 0.85, "feedback": "Good creative"},
        performance={"impressions": 1000, "clicks": 50}
    )
    
    async_session.add(creative)
    await async_session.commit()
    
    # Проверяем, что креатив создан и связан с кампанией
    result = await async_session.get(Creative, creative.id)
    assert result is not None
    assert result.fb_creative_id == "test_creative_123"
    assert result.campaign_id == campaign.id

@pytest.mark.asyncio
async def test_relationships(async_session: AsyncSession):
    from sqlalchemy import select
    
    # Создаем тестовые данные
    user = User(
        telegram_id=123456792,
        fb_access_token="test_token_4",
        fb_account_id="test_account_4"
    )
    async_session.add(user)
    await async_session.commit()
    
    campaign = Campaign(
        fb_campaign_id="test_campaign_789",
        user_id=user.id,
        name="Test Campaign 3",
        status="ACTIVE",
        objective="CONVERSIONS",
        daily_budget=300.0
    )
    async_session.add(campaign)
    await async_session.commit()
    
    creative = Creative(
        campaign_id=campaign.id,
        fb_creative_id="test_creative_456",
        type="image",
        file_path="/path/to/test/image2.jpg",
        analysis={"score": 0.9, "feedback": "Excellent creative"},
        performance={"impressions": 2000, "clicks": 100}
    )
    async_session.add(creative)
    await async_session.commit()
    
    # Проверяем связи между моделями с помощью select
    result = await async_session.execute(
        select(User).
        filter_by(id=user.id)
    )
    user = result.scalar_one()
    
    # Загружаем связи явно
    result = await async_session.execute(
        select(Campaign).
        filter_by(user_id=user.id)
    )
    campaign = result.scalar_one()
    
    result = await async_session.execute(
        select(Creative).
        filter_by(campaign_id=campaign.id)
    )
    creative = result.scalar_one()
    
    # Проверяем ID для подтверждения связей
    assert campaign.user_id == user.id
    assert creative.campaign_id == campaign.id
