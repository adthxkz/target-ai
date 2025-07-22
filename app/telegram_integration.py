import asyncio
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Загрузка переменных окружения из .env файла для локальной разработки
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
IS_PRODUCTION = os.getenv("RENDER", "false").lower() == "true"

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения экземпляра приложения
application: Application | None = None

user_states = {}

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с кнопками в ответ на команду /start."""
    keyboard = [
        [InlineKeyboardButton("🎨 Создать кампанию", callback_data="create_campaign")],
        [InlineKeyboardButton("🌐 Веб-интерфейс", url="https://target-ai-prlm.onrender.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = (
        "🎯 *Target AI Bot*\n\n"
        "Добро пожаловать! Я помогу вам проанализировать рекламные креативы.\n\n"
        "Нажмите кнопку ниже, чтобы начать создание кампании, или воспользуйтесь веб-интерфейсом."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data == "create_campaign":
        user_states[user_id] = {"state": "awaiting_media"}
        await query.answer()
        await query.edit_message_text(
            text="🎨 *Создание новой кампании*\n\nЗагрузите изображение или видео вашего креатива.",
            parse_mode='Markdown'
        )
    else:
        await query.answer()

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id, {}).get("state")
    if state != "awaiting_media":
        await update.message.reply_text("Сначала нажмите 'Создать кампанию' в меню.")
        return
    await update.message.reply_text("📊 Анализирую ваш креатив...")
    try:
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_name = f"image_{user_id}.jpg"
        elif update.message.video:
            file = await update.message.video.get_file()
            file_name = f"video_{user_id}.mp4"
        else:
            await update.message.reply_text("Пожалуйста, загрузите изображение или видео.")
            return
        file_bytes = await file.download_as_bytearray()
        # Здесь должен быть реальный анализ, пока мок
        analysis_result = await analyze_media_mock(file_bytes, file_name)
        user_states[user_id]["analysis"] = analysis_result
        user_states[user_id]["state"] = "analysis_complete"
        await update.message.reply_text(f"Результат анализа: {analysis_result}")
    except Exception as e:
        logger.error(f"Ошибка обработки медиа: {e}")
        await update.message.reply_text(f"Ошибка обработки файла: {str(e)}")

async def analyze_media_mock(file_bytes, filename):
    return {"status": "success", "filename": filename}

async def start_bot():
    """
    Инициализирует бота, настраивает обработчики и конфигурирует вебхук или поллинг.
    Эта функция вызывается при запуске приложения FastAPI.
    """
    global application
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен. Telegram бот не будет запущен.")
        return

    try:
        builder = Application.builder().token(TELEGRAM_TOKEN)
        application = builder.build()


        # Добавление обработчиков команд и событий
        application.add_handler(CommandHandler("start", start_command_handler))
        application.add_handler(CallbackQueryHandler(callback_query_handler))
        application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

        # Инициализация приложения
        await application.initialize()

        if IS_PRODUCTION:
            # Установка вебхука в продакшене
            webhook_url = f"{BASE_URL}/webhook/telegram"
            await application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=Update.ALL_TYPES
            )
            logger.info(f"Вебхук Telegram установлен на {webhook_url}")
        else:
            # Запуск поллинга в разработке
            if application.updater:
                await application.updater.start_polling()
                logger.info("Telegram бот запущен с поллингом для локальной разработки.")

        logger.info("Telegram бот успешно запущен.")

    except Exception as e:
        logger.error("Не удалось запустить Telegram бота", exc_info=True)
        application = None  # Гарантируем, что приложение не будет использоваться в случае сбоя

async def stop_bot():
    """
    Корректно останавливает бота.
    Эта функция вызывается при завершении работы приложения FastAPI.
    """
    if application:
        try:
            if IS_PRODUCTION:
                await application.bot.delete_webhook()
                logger.info("Вебхук Telegram удален.")
            else:
                if application.updater and application.updater.is_running:
                    await application.updater.stop()
                    logger.info("Поллинг Telegram остановлен.")
            
            await application.shutdown()
            logger.info("Приложение Telegram успешно завершило работу.")
        except Exception:
            logger.error("Произошла ошибка при остановке бота.", exc_info=True)

async def process_telegram_update(data: dict):
    """
    Обрабатывает одно обновление от вебхука Telegram.
    Эта функция вызывается эндпоинтом вебхука в main.py.
    """
    if not application:
        logger.warning("Бот не инициализирован; обработка обновления пропущена.")
        return

    try:
        async with application:
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
    except Exception:
        logger.error("Произошла ошибка при обработке обновления Telegram.", exc_info=True)

