from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import os

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
        ],
        [
            InlineKeyboardButton("🔄 Подключить Facebook", callback_data="connect_fb")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я помогу вам управлять рекламными кампаниями Facebook.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def campaigns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Мои кампании"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Активные", callback_data="campaigns_active"),
            InlineKeyboardButton("⏸ На паузе", callback_data="campaigns_paused")
        ],
        [
            InlineKeyboardButton("➕ Создать новую", callback_data="campaign_create")
        ],
        [
            InlineKeyboardButton("« Назад", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 *Управление кампаниями*\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_active_campaigns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ активных кампаний"""
    query = update.callback_query
    await query.answer()
    
    # В режиме разработки используем тестовые данные
    campaigns = [
        {"name": "Test Campaign 1", "status": "ACTIVE", "budget": "1000 USD"},
        {"name": "Test Campaign 2", "status": "ACTIVE", "budget": "500 USD"}
    ]
    
    text = "📈 *Активные кампании:*\n\n"
    for i, camp in enumerate(campaigns, 1):
        text += f"{i}. {camp['name']}\n"
        text += f"   Статус: {camp['status']}\n"
        text += f"   Бюджет: {camp['budget']}\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton("⏸ Приостановить", callback_data=f"pause_{i}")
            for i in range(len(campaigns))
        ],
        [
            InlineKeyboardButton("« Назад к кампаниям", callback_data="campaigns")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Бюджет"""
    query = update.callback_query
    await query.answer()
    
    # Тестовые данные о бюджете
    total_budget = 1500
    spent_today = 450
    remaining = total_budget - spent_today
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Изменить бюджет", callback_data="change_budget")
        ],
        [
            InlineKeyboardButton("📊 Статистика расходов", callback_data="budget_stats")
        ],
        [
            InlineKeyboardButton("« Назад", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 *Управление бюджетом*\n\n"
        f"Дневной бюджет: ${total_budget}\n"
        f"Потрачено сегодня: ${spent_today}\n"
        f"Осталось: ${remaining}\n\n"
        f"Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Статистика"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📅 За сегодня", callback_data="stats_today"),
            InlineKeyboardButton("📅 За неделю", callback_data="stats_week")
        ],
        [
            InlineKeyboardButton("📅 За месяц", callback_data="stats_month"),
            InlineKeyboardButton("📊 Сводный отчёт", callback_data="stats_summary")
        ],
        [
            InlineKeyboardButton("« Назад", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📈 *Статистика*\n\n"
        "Выберите период:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
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
        ],
        [
            InlineKeyboardButton("🔄 Подключить Facebook", callback_data="connect_fb")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Главное меню:\nВыберите действие:",
        reply_markup=reply_markup
    )

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Настройки"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications"),
            InlineKeyboardButton("⚙️ Общие", callback_data="settings_general")
        ],
        [
            InlineKeyboardButton("« Назад", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Настройки*\n\n"
        "Выберите раздел настроек:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def connect_fb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки Подключить Facebook"""
    query = update.callback_query
    await query.answer()
    
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    auth_url = f"{backend_url}/auth/facebook"
    
    keyboard = [
        [
            InlineKeyboardButton("🔗 Подключить аккаунт", url=auth_url)
        ],
        [
            InlineKeyboardButton("« Назад", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 *Подключение Facebook*\n\n"
        "Для подключения вашего рекламного аккаунта Facebook нажмите кнопку ниже.\n"
        "Вы будете перенаправлены на страницу авторизации Facebook.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
