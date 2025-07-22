from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from typing import Optional

# Попытка импорта сервисов
try:
    from ..services.media_analysis import MediaAnalysisService
    from ..services.campaign_automation import CampaignAutomationService
    SERVICES_AVAILABLE = True
    media_analysis_service = MediaAnalysisService()
    campaign_automation_service = CampaignAutomationService()
except ImportError:
    SERVICES_AVAILABLE = False

router = APIRouter(
    prefix="/api",
    tags=["media", "campaign"],
)

logger = logging.getLogger(__name__)

@router.post("/analyze-media")
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
                "target_audience": {"age_range": "25-45", "interests": ["технологии", "маркетинг"]},
                "campaign_objective": "CONVERSIONS",
                "ad_copy_suggestions": ["Инновационное решение для вашего бизнеса!"],
            },
            "file_info": {"filename": file.filename, "analyzed_at": datetime.now().isoformat()},
            "services_available": False
        })
    
    try:
        allowed_types = {'image': ['image/jpeg', 'image/png'], 'video': ['video/mp4', 'video/mov']}
        file_type = next((k for k, v in allowed_types.items() if file.content_type in v), None)
        
        if not file_type:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый тип файла: {file.content_type}")
        
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Файл слишком большой (макс 10MB)")
        
        analysis_func = getattr(media_analysis_service, f"analyze_{file_type}")
        analysis_result = await analysis_func(file_content, file.filename)
        
        analysis_result["file_info"] = {"filename": file.filename, "content_type": file.content_type}
        return JSONResponse(analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка анализа медиа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа файла: {str(e)}")

@router.post("/create-campaign")
async def create_campaign_from_analysis(request: Request):
    """Создает рекламную кампанию на основе результатов анализа медиа"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Сервис автоматизации кампаний недоступен.")
    try:
        data = await request.json()
        if "analysis_data" not in data:
            raise HTTPException(status_code=400, detail="Отсутствуют данные анализа")
        
        campaign_result = await campaign_automation_service.create_campaign_from_analysis(
            data["analysis_data"], data.get("user_preferences", {})
        )
        return JSONResponse(campaign_result)
    except Exception as e:
        logger.error(f"Ошибка создания кампании: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания кампании: {str(e)}")

@router.get("/campaign/{campaign_id}/performance")
async def get_campaign_performance(campaign_id: str):
    """Получает метрики производительности кампании"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Сервис автоматизации кампаний недоступен.")
    try:
        performance = await campaign_automation_service.get_campaign_performance(campaign_id)
        return JSONResponse(performance)
    except Exception as e:
        logger.error(f"Ошибка получения метрик кампании {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения метрик: {str(e)}")

@router.post("/campaign/{campaign_id}/optimize")
async def optimize_campaign(campaign_id: str):
    """Запускает оптимизацию кампании на основе текущих метрик"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Сервис автоматизации кампаний недоступен.")
    try:
        optimization_result = await campaign_automation_service.optimize_campaign(campaign_id)
        return JSONResponse(optimization_result)
    except Exception as e:
        logger.error(f"Ошибка оптимизации кампании {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка оптимизации: {str(e)}")

@router.get("/workflow/demo")
async def demo_full_workflow():
    """Демонстрирует полный рабочий процесс: анализ -> создание -> оптимизация"""
    # Эта логика может быть упрощена или вынесена в сервисный слой
    return JSONResponse({"message": "Демо-эндпоинт в процессе рефакторинга."})
