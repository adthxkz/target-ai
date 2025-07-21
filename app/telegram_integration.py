from fastapi import FastAPI, HTTPException
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import asyncio
import os
import logging
from dotenv import load_dotenv

# Импортируем обработчики из современной версии бота
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from telegram_bot_v2 import (
        start, 
        button_callback, 
        handle_media,
        BOT_TOKEN
    )
    HANDLERS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Telegram bot v2 handlers imported successfully")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import v2 handlers: {e}")
    HANDLERS_AVAILABLE = False

# Загрузка переменных окружения
if os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env")):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class TelegramBot:
    def __init__(self):
        self.app = None
        
    async def start(self):
        """Запуск бота"""
        if not TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
            
        if not self.app:
            if HANDLERS_AVAILABLE:
                # Используем современную версию с поддержкой медиа
                self.app = Application.builder().token(TELEGRAM_TOKEN).build()
                
                # Добавляем обработчики
                self.app.add_handler(CommandHandler("start", start))
                self.app.add_handler(CallbackQueryHandler(button_callback))
                self.app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
                
                logger.info("Telegram бот v2 с поддержкой медиа инициализирован")
            else:
                # Простой fallback бот без старых зависимостей
                async def simple_start(update, context):
                    await update.message.reply_text(
                        "🤖 Target AI Bot\n\n"
                        "Бот временно работает в упрощенном режиме.\n"
                        "Основные функции доступны через API:\n"
                        "https://target-ai-prlm.onrender.com"
                    )
                
                self.app = Application.builder().token(TELEGRAM_TOKEN).build()
                self.app.add_handler(CommandHandler("start", simple_start))
                logger.info("Telegram бот (простой fallback) инициализирован")
            
            # Инициализируем и запускаем
            await self.app.initialize()
            await self.app.start()
            
            # В production используем webhook, локально polling
            if os.getenv("RENDER", "false").lower() == "true":
                # Production: настраиваем webhook
                webhook_url = f"https://target-ai-prlm.onrender.com/webhook/telegram"
                await self.app.bot.set_webhook(webhook_url)
                logger.info(f"Telegram webhook установлен: {webhook_url}")
            else:
                # Локальная разработка: используем polling в отдельной задаче
                asyncio.create_task(self._run_polling())
                logger.info("Telegram polling запущен в фоновом режиме")
                
            logger.info("Telegram бот инициализирован и готов к работе")
    
    async def _run_polling(self):
        """Запуск polling в фоновом режиме для локальной разработки"""
        try:
            await self.app.updater.start_polling()
            await self.app.updater.idle()
        except Exception as e:
            logger.error(f"Ошибка polling: {e}")
            
    async def stop(self):
        """Остановка бота"""
        if self.app:
            # Удаляем webhook если был установлен
            try:
                await self.app.bot.delete_webhook()
            except:
                pass
                
            await self.app.stop()
            await self.app.shutdown()
            self.app = None
            logger.info("Telegram бот остановлен")
            
    async def stop(self):
        """Остановка бота"""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()
            self.app = None
            logger.info("Telegram бот остановлен")

bot_instance = TelegramBot()

async def start_bot():
    """Запуск бота в фоновом режиме"""
    await bot_instance.start()
