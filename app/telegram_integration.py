import asyncio
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Загрузка переменных окружения из .env файла для локальной разработки
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
IS_PRODUCTION = os.getenv("RENDER", "false").lower() == "true"

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения экземпляра приложения
application: Application | None = None

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение в ответ на команду /start."""
    welcome_message = (
        "🎯 *Target AI Bot*\n\n"
        "Добро пожаловать! Я помогу вам проанализировать рекламные креативы.\n\n"
        "Просто отправьте мне изображение или видео, чтобы начать. "
        "Для получения дополнительных возможностей используйте веб-интерфейс."
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

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

        # Добавление обработчиков команд
        application.add_handler(CommandHandler("start", start_command_handler))

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

