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
except ImportError as e:
    print(f"Не удалось импортировать обработчики v2: {e}")
    from .bot.bot import create_bot
    HANDLERS_AVAILABLE = False

# Загрузка переменных окружения
if os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env")):
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.app = None
        
    async def start(self):
        """Запуск бота"""
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
                # Fallback к старой версии
                self.app = create_bot()
                logger.info("Telegram бот v1 (fallback) инициализирован")
            
            await self.app.initialize()
            await self.app.start()
            logger.info("Telegram бот запущен")
            
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
