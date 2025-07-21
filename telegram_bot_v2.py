import asyncio
import logging
import os
import json
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Определяем API URL в зависимости от окружения
IS_PRODUCTION = os.getenv("RENDER", "false").lower() == "true"
if IS_PRODUCTION:
    API_BASE_URL = "https://target-ai-prlm.onrender.com"
else:
    API_BASE_URL = "http://localhost:5000"  # Flask API для локальной разработки

logger.info(f"Telegram бот будет использовать API: {API_BASE_URL}")

# Хранилище состояний пользователей
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📊 Мои кампании", callback_data="campaigns")],
        [InlineKeyboardButton("🎨 Создать кампанию", callback_data="create_campaign")],
        [InlineKeyboardButton("📈 Аналитика", callback_data="analytics")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("🎬 Демо workflow", callback_data="demo_workflow")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎯 *Target AI* - Ваш помощник в рекламе

Загрузите изображение или видео креатива, и я:
• Проанализирую его с помощью ИИ
• Создам оптимальную рекламную кампанию
• Запущу тестирование и оптимизацию

Выберите действие:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "campaigns":
        await show_campaigns(query, context)
    elif query.data == "create_campaign":
        await start_campaign_creation(query, context)
    elif query.data == "analytics":
        await show_analytics(query, context)
    elif query.data == "settings":
        await show_settings(query, context)
    elif query.data == "demo_workflow":
        await demo_workflow(query, context)
    elif query.data == "confirm_campaign":
        await confirm_campaign_creation(query, context)
    elif query.data == "back_to_menu":
        await show_main_menu(query, context)

async def show_campaigns(query, context):
    """Показать список кампаний"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/campaigns") as response:
                if response.status == 200:
                    data = await response.json()
                    campaigns = data.get("campaigns", [])
                    
                    if campaigns:
                        text = "*📊 Ваши кампании:*\n\n"
                        for campaign in campaigns:
                            status_emoji = "🟢" if campaign["status"] == "ACTIVE" else "🔴"
                            text += f"{status_emoji} *{campaign['name']}*\n"
                            text += f"💰 Бюджет: ${campaign['daily_budget']}/день\n"
                            text += f"🎯 Цель: {campaign['objective']}\n\n"
                    else:
                        text = "У вас пока нет кампаний. Создайте первую!"
                else:
                    text = "Ошибка загрузки кампаний"
    except Exception as e:
        text = f"Ошибка: {str(e)}"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_campaign_creation(query, context):
    """Начать создание кампании"""
    user_id = query.from_user.id
    user_states[user_id] = {"state": "awaiting_media"}
    
    text = """
🎨 *Создание новой кампании*

Загрузите изображение или видео вашего креатива.

Поддерживаемые форматы:
• 🖼️ Изображения: JPG, PNG, GIF, WebP
• 🎥 Видео: MP4, AVI, MOV

Максимальный размер файла: 10 МБ
    """
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженных медиа файлов"""
    user_id = update.from_user.id
    
    if user_id not in user_states or user_states[user_id].get("state") != "awaiting_media":
        await update.message.reply_text("Сначала нажмите 'Создать кампанию' в меню.")
        return
    
    await update.message.reply_text("📊 Анализирую ваш креатив...")
    
    try:
        # Получаем файл
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_name = f"image_{user_id}.jpg"
        elif update.message.video:
            file = await update.message.video.get_file()
            file_name = f"video_{user_id}.mp4"
        else:
            await update.message.reply_text("Пожалуйста, загрузите изображение или видео.")
            return
        
        # Скачиваем файл
        file_bytes = await file.download_as_bytearray()
        
        # Отправляем на анализ (имитация)
        analysis_result = await analyze_media_mock(file_bytes, file_name)
        
        # Сохраняем результат анализа
        user_states[user_id]["analysis"] = analysis_result
        user_states[user_id]["state"] = "analysis_complete"
        
        # Показываем результат анализа
        await show_analysis_result(update, analysis_result)
        
    except Exception as e:
        logger.error(f"Ошибка обработки медиа: {e}")
        await update.message.reply_text(f"Ошибка обработки файла: {str(e)}")

async def analyze_media_mock(file_bytes, filename):
    """Мок анализ медиа (в реальности будет вызов API)"""
    # Имитируем анализ
    return {
        "status": "success",
        "analysis": {
            "target_audience": {
                "age_range": "25-45",
                "interests": ["технологии", "инновации", "бизнес"],
                "demographics": "городская аудитория, средний доход"
            },
            "campaign_objective": "CONVERSIONS",
            "ad_copy_suggestions": [
                "Революционное решение для вашего бизнеса! 🚀",
                "Откройте новые возможности уже сегодня",
                "Присоединяйтесь к тысячам довольных клиентов"
            ],
            "budget_recommendation": {
                "daily_budget": 50,
                "currency": "USD"
            },
            "creative_insights": {
                "style": "современный, профессиональный",
                "colors": ["синий", "белый"],
                "emotions": ["доверие", "инновации"]
            }
        }
    }

async def show_analysis_result(update, analysis_result):
    """Показать результат анализа"""
    analysis = analysis_result.get("analysis", {})
    
    text = "✅ *Анализ завершен!*\n\n"
    
    # Целевая аудитория
    audience = analysis.get("target_audience", {})
    text += f"👥 *Целевая аудитория:*\n"
    text += f"• Возраст: {audience.get('age_range', 'N/A')}\n"
    text += f"• Интересы: {', '.join(audience.get('interests', []))}\n\n"
    
    # Рекомендуемый бюджет
    budget = analysis.get("budget_recommendation", {})
    text += f"💰 *Рекомендуемый бюджет:*\n"
    text += f"${budget.get('daily_budget', 0)}/день\n\n"
    
    # Варианты текста
    ad_copies = analysis.get("ad_copy_suggestions", [])
    if ad_copies:
        text += f"📝 *Варианты текста объявления:*\n"
        for i, copy in enumerate(ad_copies[:2], 1):
            text += f"{i}. {copy}\n"
        text += "\n"
    
    # Инсайты креатива
    insights = analysis.get("creative_insights", {})
    text += f"🎨 *Анализ креатива:*\n"
    text += f"• Стиль: {insights.get('style', 'N/A')}\n"
    if insights.get('colors'):
        text += f"• Цвета: {', '.join(insights['colors'])}\n"
    
    keyboard = [
        [InlineKeyboardButton("🚀 Создать кампанию", callback_data="confirm_campaign")],
        [InlineKeyboardButton("🔄 Загрузить другой файл", callback_data="create_campaign")],
        [InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def confirm_campaign_creation(query, context):
    """Подтверждение создания кампании"""
    user_id = query.from_user.id
    
    if user_id not in user_states or "analysis" not in user_states[user_id]:
        await query.edit_message_text("Ошибка: данные анализа не найдены. Начните сначала.")
        return
    
    await query.edit_message_text("🚀 Создаю кампанию на основе анализа...")
    
    try:
        # Имитируем создание кампании
        analysis_data = user_states[user_id]["analysis"]
        campaign_result = await create_campaign_mock(analysis_data)
        
        if campaign_result["status"] == "success":
            campaign = campaign_result["campaign"]
            text = f"""
✅ *Кампания создана успешно!*

📊 *{campaign['name']}*
🎯 Цель: {campaign['objective']}
💰 Бюджет: ${campaign['budget']}/день
📅 Создана: {campaign['created_at'][:10]}

🚀 Кампания автоматически запущена и начинает работу!

Вы получите уведомления о:
• Первых показах и кликах
• Рекомендациях по оптимизации
• Достижении целевых метрик
            """
        else:
            text = f"❌ Ошибка создания кампании: {campaign_result.get('message', 'Неизвестная ошибка')}"
        
        # Очищаем состояние пользователя
        user_states.pop(user_id, None)
        
    except Exception as e:
        text = f"❌ Ошибка: {str(e)}"
    
    keyboard = [[InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def create_campaign_mock(analysis_data):
    """Мок создания кампании"""
    import random
    from datetime import datetime
    
    analysis = analysis_data.get("analysis", {})
    campaign_id = f"camp_{random.randint(100000, 999999)}"
    
    return {
        "status": "success",
        "campaign": {
            "campaign_id": campaign_id,
            "name": f"AI Campaign - {datetime.now().strftime('%Y%m%d_%H%M')}",
            "objective": analysis.get("campaign_objective", "CONVERSIONS"),
            "budget": analysis.get("budget_recommendation", {}).get("daily_budget", 50),
            "created_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        }
    }

async def show_analytics(query, context):
    """Показать аналитику"""
    text = """
📈 *Аналитика кампаний*

📊 За последние 7 дней:
• Показы: 12,450
• Клики: 523
• Конверсии: 47
• CTR: 4.2%
• Стоимость клика: $1.25
• ROAS: 3.2

🎯 Лучшая кампания: "AI Campaign 001"
📉 Требует внимания: "Test Campaign 2"
    """
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_settings(query, context):
    """Показать настройки"""
    text = """
⚙️ *Настройки*

🔔 Уведомления: Включены
💰 Валюта: USD
🌍 Часовой пояс: UTC+3
🎯 Автооптимизация: Включена

📱 Уведомления приходят:
• При завершении анализа
• При изменении статуса кампании
• При достижении лимитов бюджета
• При рекомендациях оптимизации
    """
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def demo_workflow(query, context):
    """Демонстрация полного workflow"""
    await query.edit_message_text("🎬 Запускаю демонстрацию полного процесса...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/workflow/demo") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    text = "✅ *Демонстрация завершена!*\n\n"
                    text += "🎯 Процесс включал:\n"
                    text += "1. ✅ Анализ креатива ИИ\n"
                    text += "2. ✅ Создание кампании\n"
                    text += "3. ✅ Сбор метрик\n"
                    text += "4. ✅ Автооптимизация\n\n"
                    
                    workflow = data.get("workflow", {})
                    if "step_2_campaign_creation" in workflow:
                        campaign = workflow["step_2_campaign_creation"].get("campaign", {})
                        text += f"📊 Создана кампания: {campaign.get('name', 'N/A')}\n"
                        text += f"💰 Бюджет: ${campaign.get('budget', 0)}/день\n"
                    
                    if "step_4_optimization" in workflow:
                        optimizations = workflow["step_4_optimization"].get("optimizations", [])
                        if optimizations:
                            text += f"\n🔧 Рекомендации: {len(optimizations)} пунктов\n"
                else:
                    text = "❌ Ошибка демонстрации"
    except Exception as e:
        text = f"❌ Ошибка: {str(e)}"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_main_menu(query, context):
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("📊 Мои кампании", callback_data="campaigns")],
        [InlineKeyboardButton("🎨 Создать кампанию", callback_data="create_campaign")],
        [InlineKeyboardButton("📈 Аналитика", callback_data="analytics")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton("🎬 Демо workflow", callback_data="demo_workflow")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎯 *Target AI* - Главное меню

Выберите действие:
    """
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")
        return
    
    print("🤖 Запускаю Target AI Telegram Bot...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчик медиа файлов
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO, 
        handle_media
    ))
    
    # Запускаем бота
    print("✅ Target AI Bot запущен! Нажмите Ctrl+C для остановки.")
    application.run_polling()

if __name__ == "__main__":
    main()
