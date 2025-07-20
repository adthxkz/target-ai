import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    await update.message.reply_text(
        "Привет! Я бот для генерации рекламных текстов.\n\n"
        "Ты можешь:\n\n"
        "1. Отправить текстовое сообщение в формате:\n"
        "ниша, цель\n"
        "Например: электроника, продажи новых смартфонов\n\n"
        "2. Отправить фото или видео с подписью\n"
        "Я проанализирую медиафайл и помогу составить рекламный текст.\n\n"
        "Если отправляешь только цель рекламы, я буду использовать общую нишу."
    )

async def send_to_backend(message: str, file_path: Optional[Path] = None) -> dict[str, Any]:
    """Отправляет сообщение и файл (если есть) в backend и возвращает ответ."""
    async with httpx.AsyncClient() as client:
        try:
            if file_path:
                # Отправляем файл и сообщение через multipart/form-data
                files = {'file': open(file_path, 'rb')}
                data = {'message': message} if message else {}
                response = await client.post(
                    f"{BACKEND_URL}/upload",
                    files=files,
                    data=data,
                    timeout=30.0
                )
            else:
                # Стандартный запрос для текстового сообщения
                parts = message.split(',', 1)
                if len(parts) == 2:
                    niche, goal = parts
                else:
                    niche = "общая"
                    goal = message

                response = await client.post(
                    f"{BACKEND_URL}/generate_ad",
                    json={
                        "niche": niche.strip(),
                        "goal": goal.strip()
                    },
                    timeout=30.0
                )
            
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Ошибка при отправке запроса: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP: {str(e)}")
            raise
        finally:
            if file_path and file_path.exists():
                try:
                    file_path.unlink()  # Удаляем временный файл
                except Exception as e:
                    logger.warning(f"Не удалось удалить временный файл {file_path}: {e}")

async def process_media(update: Update, file_obj: Any, media_type: str) -> None:
    """Обрабатывает медиафайлы (фото или видео)."""
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    caption = update.message.caption or ""

    logger.info(f"Получен {media_type} от пользователя {username} (ID: {user_id})")

    try:
        # Создаем временную директорию, если её нет
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)

        # Скачиваем файл
        file = await file_obj.get_file()
        extension = ".jpg" if media_type == "фото" else ".mp4"
        tmp_file = tmp_dir / f"temp_{user_id}_{file.file_unique_id}{extension}"
        
        await file.download_to_drive(tmp_file)
        logger.info(f"Файл сохранен как {tmp_file}")

        # Отправляем индикатор обработки
        await update.message.chat.send_action('typing')

        # Отправляем файл и caption в backend
        response_data = await send_to_backend(caption, tmp_file)

        # Форматируем и отправляем ответ пользователю
        try:
            response_json = response_data["response"]
            if isinstance(response_json, str):
                import json
                data = json.loads(response_json)
                formatted_response = (
                    f"📌 *Заголовок:*\n{data['title']}\n\n"
                    f"📝 *Описание:*\n{data['description']}\n\n"
                    f"👥 *Целевая аудитория:*\n{data['audience']}"
                )
            else:
                formatted_response = response_json
            await update.message.reply_text(formatted_response, parse_mode='Markdown')
        except (json.JSONDecodeError, KeyError):
            # Если не удалось распарсить JSON, отправляем как есть
            await update.message.reply_text(response_data["response"])
        
        logger.info(f"Отправлен ответ пользователю {username} (ID: {user_id})")

    except Exception as e:
        error_message = "Извините, произошла ошибка при обработке вашего файла. Попробуйте позже."
        await update.message.reply_text(error_message)
        logger.error(f"Ошибка при обработке {media_type} от {username} (ID: {user_id}): {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает входящие сообщения."""
    if update.message.photo:
        # Берем последнее фото (самого высокого качества)
        await process_media(update, update.message.photo[-1], "фото")
        return

    if update.message.video:
        await process_media(update, update.message.video, "видео")
        return

    # Обработка текстового сообщения
    user_message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    logger.info(f"Получено сообщение от пользователя {username} (ID: {user_id}): {user_message}")

    try:
        # Отправляем индикатор набора текста
        await update.message.chat.send_action('typing')
        
        # Отправляем запрос в backend
        response_data = await send_to_backend(user_message)
        
        # Форматируем и отправляем ответ пользователю
        try:
            response_json = response_data["response"]
            if isinstance(response_json, str):
                import json
                data = json.loads(response_json)
                formatted_response = (
                    f"📌 *Заголовок:*\n{data['title']}\n\n"
                    f"📝 *Описание:*\n{data['description']}\n\n"
                    f"👥 *Целевая аудитория:*\n{data['audience']}"
                )
            else:
                formatted_response = response_json
            await update.message.reply_text(formatted_response, parse_mode='Markdown')
        except (json.JSONDecodeError, KeyError):
            # Если не удалось распарсить JSON, отправляем как есть
            await update.message.reply_text(response_data["response"])
        
        logger.info(f"Отправлен ответ пользователю {username} (ID: {user_id})")
    
    except Exception as e:
        error_message = "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
        await update.message.reply_text(error_message)
        logger.error(f"Ошибка при обработке сообщения от {username} (ID: {user_id}): {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ошибки."""
    logger.error(f"Произошла ошибка: {context.error}")

def main() -> None:
    """Запускает бота."""
    # Проверяем наличие токена
    if not TELEGRAM_TOKEN:
        logger.error("Telegram bot token не найден в переменных окружения")
        sys.exit(1)

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | (filters.TEXT & ~filters.COMMAND),
        handle_message
    ))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
