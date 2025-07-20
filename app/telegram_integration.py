from fastapi import FastAPI, HTTPException
from telegram.ext import Application
import asyncio
import os
from dotenv import load_dotenv
from .bot.bot import create_bot

# Загрузка переменных окружения
if os.path.exists(".env"):
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

class TelegramBot:
    def __init__(self):
        self.app = None
        
    async def start(self):
        """Запуск бота"""
        if not self.app:
            self.app = create_bot()
            await self.app.initialize()
            await self.app.start()
            await self.app.update_bot_data({"campaigns": {}})
            
    async def stop(self):
        """Остановка бота"""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()
            self.app = None

bot_instance = TelegramBot()

async def start_bot():
    """Запуск бота в фоновом режиме"""
    await bot_instance.start()
