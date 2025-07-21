from fastapi import FastAPI, HTTPException
from telegram.ext import Application, CommandHandler
import asyncio
import os
import logging
from dotenv import load_dotenv

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
        if not TELEGRAM_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return
            
        try:
            if not self.app:
                # Создаем простой бот без сложных зависимостей
                self.app = Application.builder().token(TELEGRAM_TOKEN).build()
                
                # Добавляем простой обработчик start
                async def simple_start(update, context):
                    await update.message.reply_text(
                        "🎯 *Target AI Bot*\n\n"
                        "Добро пожаловать в Target AI!\n\n"
                        "🚀 Основные функции:\n"
                        "• AI анализ медиа контента\n"
                        "• Автоматизация Facebook Ads\n"
                        "• Оптимизация кампаний\n\n"
                        "💻 Используйте веб-интерфейс для полного функционала:\n"
                        "🌐 https://target-ai-prlm.onrender.com\n"
                        "📊 https://target-ai-prlm.onrender.com/docs",
                        parse_mode='Markdown'
                    )
                
                self.app.add_handler(CommandHandler("start", simple_start))
                logger.info("Telegram бот (упрощенная версия) инициализирован")
            
            # Инициализируем приложение
            await self.app.initialize()
            logger.info("Telegram бот успешно инициализирован")
            
            # В production настраиваем webhook
            if os.getenv("RENDER", "false").lower() == "true":
                webhook_url = f"https://target-ai-prlm.onrender.com/webhook/telegram"
                await self.app.bot.set_webhook(webhook_url)
                logger.info(f"Telegram webhook установлен: {webhook_url}")
            else:
                logger.info("Локальная разработка: webhook не устанавливается")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram бота: {e}")
            # Не падаем, продолжаем работу API без бота
            
    async def stop(self):
        """Остановка бота"""
        if self.app:
            try:
                await self.app.bot.delete_webhook()
                await self.app.stop()
                await self.app.shutdown()
                self.app = None
                logger.info("Telegram бот остановлен")
            except Exception as e:
                logger.error(f"Ошибка остановки бота: {e}")

# Глобальный экземпляр бота
bot_instance = TelegramBot()

async def start_bot():
    """Функция для запуска бота из main.py"""
    await bot_instance.start()
