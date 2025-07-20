from typing import List, Dict, Optional
from datetime import datetime, timedelta

class BudgetOptimizer:
    def __init__(self, total_budget: float, daily_budget: float):
        self.total_budget = total_budget
        self.daily_budget = daily_budget
        self.campaign_budgets = {}
        self.performance_history = {}

    def calculate_campaign_budget(
        self,
        campaign_id: str,
        performance_metrics: Dict,
        days_history: int = 7
    ) -> float:
        """
        Рассчитывает оптимальный бюджет для кампании на основе её эффективности.
        
        Args:
            campaign_id: ID кампании
            performance_metrics: Метрики производительности (ROAS, CTR, конверсии и т.д.)
            days_history: Количество дней для анализа исторических данных
        
        Returns:
            float: Рекомендуемый дневной бюджет для кампании
        """
        roas = performance_metrics.get('roas', 0)
        ctr = performance_metrics.get('ctr', 0)
        conversion_rate = performance_metrics.get('conversion_rate', 0)
        
        # Базовая оценка эффективности
        performance_score = (
            roas * 0.5 +  # ROAS имеет наибольший вес
            ctr * 0.3 +   # CTR также важен
            conversion_rate * 0.2  # Конверсия тоже учитывается
        )
        
        # Сохраняем историю производительности
        if campaign_id not in self.performance_history:
            self.performance_history[campaign_id] = []
        
        self.performance_history[campaign_id].append({
            'date': datetime.now(),
            'score': performance_score
        })
        
        # Очищаем старые записи
        cutoff_date = datetime.now() - timedelta(days=days_history)
        self.performance_history[campaign_id] = [
            record for record in self.performance_history[campaign_id]
            if record['date'] >= cutoff_date
        ]
        
        # Рассчитываем тренд производительности
        if len(self.performance_history[campaign_id]) > 1:
            old_score = self.performance_history[campaign_id][0]['score']
            new_score = self.performance_history[campaign_id][-1]['score']
            trend = (new_score - old_score) / old_score if old_score > 0 else 0
        else:
            trend = 0
        
        # Определяем коэффициент корректировки бюджета
        if performance_score > 1.5:  # Отличная производительность
            budget_multiplier = 1.2
        elif performance_score > 1.0:  # Хорошая производительность
            budget_multiplier = 1.1
        elif performance_score > 0.8:  # Удовлетворительная производительность
            budget_multiplier = 1.0
        else:  # Низкая производительность
            budget_multiplier = 0.8
        
        # Учитываем тренд
        if trend > 0.1:  # Положительный тренд
            budget_multiplier *= 1.1
        elif trend < -0.1:  # Отрицательный тренд
            budget_multiplier *= 0.9
        
        # Получаем текущий бюджет кампании
        current_budget = self.campaign_budgets.get(campaign_id, self.daily_budget / len(self.campaign_budgets) if self.campaign_budgets else self.daily_budget)
        
        # Рассчитываем новый бюджет
        new_budget = current_budget * budget_multiplier
        
        # Проверяем ограничения
        min_budget = self.daily_budget * 0.1  # Минимум 10% от дневного бюджета
        max_budget = self.daily_budget * 0.5  # Максимум 50% от дневного бюджета
        
        new_budget = max(min_budget, min(new_budget, max_budget))
        
        return new_budget

    def optimize_campaign_budgets(
        self,
        campaign_metrics: List[Dict]
    ) -> Dict[str, float]:
        """
        Оптимизирует распределение бюджета между всеми кампаниями.
        
        Args:
            campaign_metrics: Список словарей с метриками по каждой кампании
        
        Returns:
            Dict[str, float]: Словарь с рекомендуемыми бюджетами для каждой кампании
        """
        total_allocated = 0
        new_budgets = {}
        
        # Первый проход: рассчитываем рекомендуемые бюджеты
        for campaign in campaign_metrics:
            campaign_id = campaign['campaign_id']
            recommended_budget = self.calculate_campaign_budget(
                campaign_id,
                campaign
            )
            new_budgets[campaign_id] = recommended_budget
            total_allocated += recommended_budget
        
        # Если сумма превышает дневной бюджет, корректируем пропорционально
        if total_allocated > self.daily_budget:
            ratio = self.daily_budget / total_allocated
            for campaign_id in new_budgets:
                new_budgets[campaign_id] *= ratio
        
        # Обновляем текущие бюджеты
        self.campaign_budgets = new_budgets
        
        return new_budgets

    def get_campaign_recommendations(
        self,
        campaign_id: str,
        performance_metrics: Dict
    ) -> Dict:
        """
        Генерирует рекомендации по оптимизации кампании.
        
        Args:
            campaign_id: ID кампании
            performance_metrics: Метрики производительности
        
        Returns:
            Dict: Рекомендации по оптимизации
        """
        roas = performance_metrics.get('roas', 0)
        ctr = performance_metrics.get('ctr', 0)
        conversion_rate = performance_metrics.get('conversion_rate', 0)
        
        recommendations = {
            'budget_change': None,
            'status': None,
            'optimization_tips': []
        }
        
        # Анализ ROAS
        if roas < 1:
            recommendations['optimization_tips'].append(
                "Низкий ROAS. Рекомендуется пересмотреть таргетинг и креативы."
            )
            recommendations['status'] = 'warning'
        elif roas > 2:
            recommendations['optimization_tips'].append(
                "Отличный ROAS. Рекомендуется увеличить бюджет для масштабирования."
            )
            recommendations['status'] = 'success'
        
        # Анализ CTR
        if ctr < 0.01:
            recommendations['optimization_tips'].append(
                "Низкий CTR. Рекомендуется улучшить креативы и заголовки."
            )
            recommendations['status'] = 'warning'
        
        # Анализ конверсии
        if conversion_rate < 0.02:
            recommendations['optimization_tips'].append(
                "Низкая конверсия. Проверьте релевантность целевой аудитории."
            )
        
        return recommendations
