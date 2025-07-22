from fastapi import APIRouter, Request, HTTPException
import logging
import json

from ..config import settings
from ..telegram_integration import process_telegram_update

router = APIRouter(
    tags=["telegram"],
)

logger = logging.getLogger(__name__)

@router.post("/webhook/telegram")
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
