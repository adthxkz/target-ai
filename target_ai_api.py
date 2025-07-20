from flask import Flask, jsonify, request
import logging
from datetime import datetime
import json
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Тестовые данные
MOCK_CAMPAIGNS = [
    {
        "id": "123456789",
        "name": "Test Campaign 1",
        "status": "ACTIVE",
        "objective": "CONVERSIONS",
        "daily_budget": 1000,
        "lifetime_budget": 10000,
        "start_time": "2025-07-01T00:00:00+0000",
        "end_time": "2025-07-31T23:59:59+0000"
    },
    {
        "id": "987654321",
        "name": "Test Campaign 2",
        "status": "PAUSED",
        "objective": "TRAFFIC",
        "daily_budget": 500,
        "lifetime_budget": 5000,
        "start_time": "2025-07-15T00:00:00+0000",
        "end_time": "2025-08-15T23:59:59+0000"
    }
]

@app.route('/health')
def health_check():
    """Проверка работоспособности API"""
    return jsonify({"status": "healthy", "timestamp": str(datetime.now())})

@app.route('/test')
def test_endpoint():
    """Тестовый эндпоинт"""
    return jsonify({"message": "Test endpoint works!", "timestamp": str(datetime.now())})

@app.route('/campaigns')
def get_campaigns():
    """Получение списка кампаний"""
    return jsonify({"campaigns": MOCK_CAMPAIGNS})

@app.route('/api/workflow/demo')
def demo_workflow():
    """Демонстрация полного workflow"""
    try:
        # 1. Мок анализ
        mock_analysis = {
            "status": "success",
            "analysis": {
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["технологии", "инновации", "бизнес"],
                    "behaviors": ["частые покупки онлайн", "интерес к новым продуктам"],
                    "demographics": "городское население, средний и выше средний доход"
                },
                "campaign_objective": "CONVERSIONS",
                "ad_copy_suggestions": [
                    "Революционное решение для вашего бизнеса",
                    "Откройте новые возможности с нашим продуктом",
                    "Присоединяйтесь к тысячам довольных клиентов"
                ],
                "budget_recommendation": {
                    "daily_budget": 50,
                    "currency": "USD",
                    "reasoning": "Оптимальный стартовый бюджет для тестирования"
                },
                "placement_suggestions": [
                    "Facebook Feed",
                    "Instagram Feed", 
                    "Instagram Stories"
                ],
                "creative_insights": {
                    "style": "современный, минималистичный",
                    "colors": ["синий", "белый", "серый"],
                    "emotions": ["доверие", "профессионализм", "инновации"],
                    "visual_elements": ["логотип", "продукт", "люди"]
                },
                "keywords": ["инновации", "технологии", "эффективность", "качество"]
            }
        }
        
        # 2. Создание кампании
        campaign_id = f"camp_{random.randint(100000, 999999)}"
        campaign_result = {
            "status": "success",
            "campaign": {
                "campaign_id": campaign_id,
                "name": f"AI Generated Campaign - {datetime.now().strftime('%Y%m%d_%H%M')}",
                "status": "ACTIVE",
                "objective": "CONVERSIONS",
                "budget": 50,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # 3. Метрики производительности
        performance = {
            "status": "success",
            "campaign_id": campaign_id,
            "total_metrics": {
                "total_impressions": random.randint(1000, 5000),
                "total_clicks": random.randint(50, 200),
                "total_conversions": random.randint(5, 25),
                "total_spend": round(random.uniform(40, 80), 2),
                "ctr": round(random.uniform(2.0, 5.0), 2),
                "cost_per_click": round(random.uniform(0.8, 2.5), 2),
                "cost_per_conversion": round(random.uniform(15, 40), 2),
                "conversion_rate": round(random.uniform(3.0, 8.0), 2)
            }
        }
        
        # 4. Оптимизация
        optimizations = []
        if performance["total_metrics"]["ctr"] < 3.0:
            optimizations.append({
                "type": "creative_optimization",
                "message": "CTR можно улучшить, обновив креатив",
                "action": "update_creative",
                "priority": "medium"
            })
        
        if performance["total_metrics"]["cost_per_conversion"] > 30:
            optimizations.append({
                "type": "targeting_optimization", 
                "message": "Рекомендуется сузить целевую аудиторию",
                "action": "refine_targeting",
                "priority": "high"
            })
        
        optimization_result = {
            "status": "success",
            "campaign_id": campaign_id,
            "optimizations": optimizations,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "workflow": {
                "step_1_analysis": mock_analysis,
                "step_2_campaign_creation": campaign_result,
                "step_3_performance": performance,
                "step_4_optimization": optimization_result
            },
            "message": "Демонстрация полного рабочего процесса завершена"
        })
        
    except Exception as e:
        logger.error(f"Ошибка демонстрации workflow: {e}")
        return jsonify({
            "status": "error",
            "message": f"Ошибка демонстрации: {str(e)}"
        }), 500

@app.route('/api/analyze-media', methods=['POST'])
def analyze_media():
    """Анализ медиа-файлов"""
    try:
        # В реальной реализации здесь будет обработка файла
        # Пока возвращаем мок данные
        return jsonify({
            "status": "success",
            "analysis": {
                "target_audience": {
                    "age_range": "25-45",
                    "interests": ["технологии", "маркетинг", "бизнес"],
                    "demographics": "профессионалы, городская аудитория"
                },
                "campaign_objective": "CONVERSIONS",
                "ad_copy_suggestions": [
                    "Инновационное решение для вашего бизнеса!",
                    "Увеличьте эффективность уже сегодня",
                    "Доверьтесь экспертам в своей области"
                ],
                "budget_recommendation": {
                    "daily_budget": 75,
                    "currency": "USD"
                },
                "creative_insights": {
                    "style": "профессиональный, современный",
                    "colors": ["синий", "белый", "серый"],
                    "emotions": ["доверие", "уверенность", "профессионализм"]
                }
            },
            "file_info": {
                "filename": "uploaded_media",
                "analyzed_at": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Ошибка анализа медиа: {e}")
        return jsonify({
            "status": "error",
            "message": f"Ошибка анализа: {str(e)}"
        }), 500

@app.route('/api/create-campaign', methods=['POST'])
def create_campaign():
    """Создание кампании на основе анализа"""
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        user_preferences = data.get('user_preferences', {})
        
        # Генерируем ID кампании
        campaign_id = f"camp_{random.randint(100000, 999999)}"
        
        # Создаем кампанию на основе анализа
        analysis = analysis_data.get('analysis', {})
        
        campaign = {
            "campaign_id": campaign_id,
            "name": user_preferences.get('campaign_name', f"AI Campaign - {datetime.now().strftime('%Y%m%d_%H%M')}"),
            "status": "ACTIVE",
            "objective": analysis.get('campaign_objective', 'CONVERSIONS'),
            "budget": user_preferences.get('budget', analysis.get('budget_recommendation', {}).get('daily_budget', 50)),
            "target_audience": analysis.get('target_audience', {}),
            "ad_copy": analysis.get('ad_copy_suggestions', ['Default ad copy'])[0],
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": "Кампания создана успешно",
            "campaign": campaign
        })
        
    except Exception as e:
        logger.error(f"Ошибка создания кампании: {e}")
        return jsonify({
            "status": "error",
            "message": f"Ошибка создания кампании: {str(e)}"
        }), 500

@app.route('/api/campaign/<campaign_id>/performance')
def get_campaign_performance(campaign_id):
    """Получение метрик кампании"""
    try:
        # Генерируем мок метрики
        metrics = {
            "total_impressions": random.randint(1000, 10000),
            "total_clicks": random.randint(50, 500),
            "total_conversions": random.randint(5, 50),
            "total_spend": round(random.uniform(30, 150), 2)
        }
        
        # Рассчитываем производные метрики
        metrics["ctr"] = round((metrics["total_clicks"] / metrics["total_impressions"]) * 100, 2) if metrics["total_impressions"] > 0 else 0
        metrics["cost_per_click"] = round(metrics["total_spend"] / metrics["total_clicks"], 2) if metrics["total_clicks"] > 0 else 0
        metrics["cost_per_conversion"] = round(metrics["total_spend"] / metrics["total_conversions"], 2) if metrics["total_conversions"] > 0 else 0
        metrics["conversion_rate"] = round((metrics["total_conversions"] / metrics["total_clicks"]) * 100, 2) if metrics["total_clicks"] > 0 else 0
        
        return jsonify({
            "status": "success",
            "campaign_id": campaign_id,
            "total_metrics": metrics,
            "period": "last_7_days",
            "updated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик: {e}")
        return jsonify({
            "status": "error",
            "message": f"Ошибка получения метрик: {str(e)}"
        }), 500

@app.route('/api/campaign/<campaign_id>/optimize', methods=['POST'])
def optimize_campaign(campaign_id):
    """Оптимизация кампании"""
    try:
        # Получаем текущие метрики для анализа
        metrics = {
            "ctr": random.uniform(1.0, 5.0),
            "cost_per_conversion": random.uniform(10, 100),
            "conversion_rate": random.uniform(1.0, 10.0)
        }
        
        optimizations = []
        
        if metrics["ctr"] < 2.0:
            optimizations.append({
                "type": "creative_optimization",
                "message": "Низкий CTR. Рекомендуется обновить креатив",
                "action": "update_creative",
                "priority": "high"
            })
        
        if metrics["cost_per_conversion"] > 50:
            optimizations.append({
                "type": "targeting_optimization", 
                "message": "Высокая стоимость конверсии. Рекомендуется сузить аудиторию",
                "action": "refine_targeting",
                "priority": "medium"
            })
        
        if metrics["conversion_rate"] < 2.0:
            optimizations.append({
                "type": "landing_page_optimization",
                "message": "Низкий коэффициент конверсии. Проверьте посадочную страницу",
                "action": "optimize_landing_page",
                "priority": "high"
            })
        
        return jsonify({
            "status": "success",
            "campaign_id": campaign_id,
            "optimizations": optimizations,
            "analyzed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Ошибка оптимизации: {e}")
        return jsonify({
            "status": "error",
            "message": f"Ошибка оптимизации: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Запускаю Target AI Flask API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
