from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import os
from dotenv import load_dotenv
from .handlers import (
    start_command,
    campaigns_handler,
    show_active_campaigns,
    budget_handler,
    stats_handler,
    back_to_main
)

# Загрузка переменных окружения
if os.path.exists(".env"):
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def create_bot():
    """Создание и настройка бота"""
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    
    # Добавляем обработчики callback-запросов
    app.add_handler(CallbackQueryHandler(campaigns_handler, pattern="^campaigns$"))
    app.add_handler(CallbackQueryHandler(show_active_campaigns, pattern="^campaigns_active$"))
    app.add_handler(CallbackQueryHandler(budget_handler, pattern="^budget$"))
    app.add_handler(CallbackQueryHandler(stats_handler, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    
    return app

def run_bot():
    """Запуск бота"""
    app = create_bot()
    print("Bot is starting...")
    app.run_polling()
