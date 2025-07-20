import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загрузка переменных окружения
if os.path.exists(".env"):
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Тестовые данные
MOCK_CAMPAIGNS = [
    {
        "id": "123456789",
        "name": "Test Campaign 1",
        "status": "ACTIVE",
        "objective": "CONVERSIONS",
        "daily_budget": 1000,
        "lifetime_budget": 10000
    },
    {
        "id": "987654321",
        "name": "Test Campaign 2",
        "status": "PAUSED",
        "objective": "TRAFFIC",
        "daily_budget": 500,
        "lifetime_budget": 5000
    }
]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Мои кампании", callback_data="campaigns"),
            InlineKeyboardButton("💰 Бюджет", callback_data="budget")
        ],
        [
            InlineKeyboardButton("📈 Статистика", callback_data="stats"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я помогу вам управлять рекламными кампаниями Facebook.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def campaigns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать кампании"""
    query = update.callback_query
    await query.answer()
    
    campaigns_text = "📊 *Ваши кампании:*\n\n"
    for campaign in MOCK_CAMPAIGNS:
        status_emoji = "✅" if campaign["status"] == "ACTIVE" else "⏸"
        campaigns_text += f"{status_emoji} *{campaign['name']}*\n"
        campaigns_text += f"   ID: {campaign['id']}\n"
        campaigns_text += f"   Статус: {campaign['status']}\n"
        campaigns_text += f"   Дневной бюджет: ${campaign['daily_budget']}\n\n"
    
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        campaigns_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать бюджет"""
    query = update.callback_query
    await query.answer()
    
    total_daily = sum(c["daily_budget"] for c in MOCK_CAMPAIGNS if c["status"] == "ACTIVE")
    total_lifetime = sum(c["lifetime_budget"] for c in MOCK_CAMPAIGNS)
    
    budget_text = f"💰 *Бюджет:*\n\n"
    budget_text += f"Общий дневной бюджет активных кампаний: *${total_daily}*\n"
    budget_text += f"Общий лайфтайм бюджет: *${total_lifetime}*\n\n"
    budget_text += f"Активных кампаний: {len([c for c in MOCK_CAMPAIGNS if c['status'] == 'ACTIVE'])}\n"
    budget_text += f"Всего кампаний: {len(MOCK_CAMPAIGNS)}"
    
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        budget_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    query = update.callback_query
    await query.answer()
    
    stats_text = "📈 *Статистика:*\n\n"
    stats_text += "🔄 Это демо-режим. Статистика будет доступна после подключения к реальному аккаунту Facebook.\n\n"
    stats_text += "Доступные метрики:\n"
    stats_text += "• Показы\n• Клики\n• CTR\n• CPC\n• Конверсии\n• ROAS"
    
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать настройки"""
    query = update.callback_query
    await query.answer()
    
    settings_text = "⚙️ *Настройки:*\n\n"
    settings_text += "🔄 Режим: Демо\n"
    settings_text += "📱 Уведомления: Включены\n"
    settings_text += "🌐 Язык: Русский\n\n"
    settings_text += "Для подключения реального аккаунта Facebook используйте веб-интерфейс."
    
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        settings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться в главное меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Мои кампании", callback_data="campaigns"),
            InlineKeyboardButton("💰 Бюджет", callback_data="budget")
        ],
        [
            InlineKeyboardButton("📈 Статистика", callback_data="stats"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👋 Главное меню:\nВыберите действие:",
        reply_markup=reply_markup
    )

def main():
    """Основная функция"""
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в .env файле")
        return
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(campaigns_handler, pattern="^campaigns$"))
    app.add_handler(CallbackQueryHandler(budget_handler, pattern="^budget$"))
    app.add_handler(CallbackQueryHandler(stats_handler, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(settings_handler, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    
    print("🤖 Target AI Telegram Bot запущен...")
    print("💬 Найдите бота в Telegram и отправьте /start")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
