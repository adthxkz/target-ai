from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.services.facebook_ads import FacebookAdsService
from app.services.budget_optimizer import BudgetOptimizer
from app.chatgpt import analyze_image, generate_ad_text
from app.schemas import (
    AdAccountConnect, CampaignCreate, CreativeUpload,
    BudgetSettings, CampaignStats, CampaignOptimization,
    DashboardMetrics
)
from app.models import AdRequest, AdResponse
from app.db.models import User, Campaign, Creative, Budget
import json

router = APIRouter()

@router.post("/facebook/connect", status_code=201)
async def connect_facebook_account(
    account_data: AdAccountConnect,
    session: AsyncSession = Depends(get_session)
):
    """Подключение Facebook Ad Account к системе"""
    try:
        # Проверяем подключение к Facebook
        fb_service = FacebookAdsService()
        fb_service.access_token = account_data.access_token
        fb_service.ad_account_id = account_data.account_id
        
        # Проверяем доступ к аккаунту
        account_info = await fb_service.get_account_info()
        
        # Создаем или обновляем пользователя
        user = User(
            fb_access_token=account_data.access_token,
            fb_account_id=account_data.account_id
        )
        session.add(user)
        await session.commit()
        
        return {
            "status": "success",
            "account_info": account_info,
            "user_id": user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка подключения к Facebook: {str(e)}"
        )

@router.post("/generate_ad", response_model=AdResponse)
async def generate_ad(request: AdRequest):
    try:
        result = await generate_ad_text(request.niche, request.goal)
        if isinstance(result["response"], str):
            result["response"] = result["response"].encode('utf-8').decode('utf-8')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns", status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    """Создание новой рекламной кампании"""
    try:
        # Получаем сервис Facebook Ads
        fb_service = FacebookAdsService()
        
        # Создаем кампанию в Facebook
        campaign_result = await fb_service.create_campaign(
            name=campaign_data.name,
            objective=campaign_data.objective,
            daily_budget=campaign_data.daily_budget,
            status=campaign_data.status
        )
        
        # Сохраняем информацию в базу данных
        campaign = Campaign(
            fb_campaign_id=campaign_result["campaign_id"],
            name=campaign_data.name,
            status=campaign_data.status,
            objective=campaign_data.objective,
            daily_budget=campaign_data.daily_budget
        )
        session.add(campaign)
        await session.commit()
        
        return {
            "status": "success",
            "campaign_id": campaign_result["campaign_id"],
            "name": campaign_data.name
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка создания кампании: {str(e)}"
        )

@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Получение информации о кампании"""
    try:
        # Получаем кампанию из базы данных
        result = await session.execute(
            select(Campaign).filter(Campaign.fb_campaign_id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Кампания не найдена")
        
        # Получаем актуальные данные из Facebook
        fb_service = FacebookAdsService()
        campaign_stats = await fb_service.get_campaign_stats(campaign_id)
        
        return {
            **campaign_stats,
            "id": campaign.id,
            "fb_campaign_id": campaign.fb_campaign_id,
            "name": campaign.name,
            "status": campaign.status,
            "objective": campaign.objective,
            "daily_budget": campaign.daily_budget
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка получения информации о кампании: {str(e)}"
        )

@router.post("/upload", response_model=AdResponse)
async def upload_file(
    file: UploadFile = File(...),
    message: Optional[str] = Form(None)
):
    try:
        content = await file.read()
        content_type = file.content_type
        print(f"Получен файл типа: {content_type}")
        
        if content_type and content_type.startswith('image/'):
            print("Обрабатываем как изображение")
            try:
                result = await analyze_image(content)
                print("Анализ изображения завершен")
                return result
            except Exception as vision_error:
                print(f"Ошибка при анализе изображения: {str(vision_error)}")
                raise
        else:
            print("Обрабатываем как обычный файл")
            goal = message if message else "анализ медиафайла"
            result = await generate_ad_text("медиа", goal)
            return result
            
    except Exception as e:
        error_msg = f"Ошибка при обработке файла: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Новые маршруты для Facebook Ads API
@router.post("/connect_ad_account")
async def connect_ad_account(
    connection: AdAccountConnect,
    session: AsyncSession = Depends(get_session)
):
    try:
        fb_service = FacebookAdsService()
        account_info = await fb_service.verify_account(
            connection.access_token,
            connection.account_id
        )
        
        user = User(
            fb_access_token=connection.access_token,
            fb_account_id=connection.account_id
        )
        session.add(user)
        await session.commit()
        
        return {"status": "success", "account_info": account_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns", response_model=dict)
async def create_campaign(
    campaign: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    try:
        fb_service = FacebookAdsService()
        result = await fb_service.create_campaign(
            name=campaign.name,
            objective=campaign.objective,
            daily_budget=campaign.daily_budget,
            status=campaign.status
        )
        
        db_campaign = Campaign(
            fb_campaign_id=result["campaign_id"],
            name=campaign.name,
            objective=campaign.objective,
            daily_budget=campaign.daily_budget,
            status=campaign.status
        )
        session.add(db_campaign)
        await session.commit()
        
        return {"status": "success", "campaign_id": result["campaign_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creatives", response_model=dict)
async def upload_creative(
    creative: CreativeUpload,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        content = await file.read()
        
        if creative.file_type == "image":
            analysis = await analyze_image(content)
        else:
            analysis = await generate_ad_text("медиа", "анализ видео")
        
        fb_service = FacebookAdsService()
        result = await fb_service.upload_creative(
            file_content=content,
            file_type=creative.file_type,
            title=creative.title,
            description=creative.description
        )
        
        db_creative = Creative(
            campaign_id=creative.campaign_id,
            fb_creative_id=result["creative_id"],
            type=creative.file_type,
            analysis=analysis
        )
        session.add(db_creative)
        await session.commit()
        
        return {
            "status": "success",
            "creative_id": result["creative_id"],
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget", response_model=dict)
async def set_budget(
    settings: BudgetSettings,
    session: AsyncSession = Depends(get_session)
):
    try:
        optimizer = BudgetOptimizer(
            settings.total_budget,
            settings.daily_budget
        )
        
        db_budget = Budget(
            total_budget=settings.total_budget,
            daily_budget=settings.daily_budget,
            start_date=settings.start_date,
            end_date=settings.end_date,
            spend_strategy=settings.campaign_distribution
        )
        session.add(db_budget)
        await session.commit()
        
        return {"status": "success", "budget_id": db_budget.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    try:
        fb_service = FacebookAdsService()
        stats = await fb_service.get_campaign_stats(campaign_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    session: AsyncSession = Depends(get_session)
):
    try:
        fb_service = FacebookAdsService()
        metrics = await fb_service.get_account_metrics()
        
        optimizer = BudgetOptimizer(
            metrics["total_budget"],
            metrics["daily_budget"]
        )
        optimizations = await optimizer.optimize_campaign_budgets(
            metrics["campaigns"]
        )
        
        return {
            "total_spend": metrics["total_spend"],
            "total_revenue": metrics["total_revenue"],
            "overall_roas": metrics["overall_roas"],
            "active_campaigns": metrics["active_campaigns"],
            "top_performing_campaigns": metrics["top_campaigns"],
            "recent_optimizations": optimizations,
            "budget_allocation": metrics["budget_allocation"],
            "performance_trend": metrics["performance_trend"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
