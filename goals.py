"""
Модуль для расчета прогресса по целям.
Здесь логика определения того, насколько вы опережаете или отстаете от плана.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from database_supabase import SupabaseDatabase


class GoalsCalculator:
    """Класс для расчета прогресса по целям"""
    
    def __init__(self, db: SupabaseDatabase):
        """
        Инициализация калькулятора
        
        Args:
            db: объект базы данных Supabase
        """
        self.db = db
    
    def day_of_year(self) -> int:
        """
        Получить текущий день года (1-365/366)
        
        Returns:
            номер дня года
        """
        return date.today().timetuple().tm_yday
    
    def days_until(self, deadline_str: Optional[str]) -> Optional[int]:
        """
        Вычислить количество дней до дедлайна
        
        Args:
            deadline_str: дата дедлайна в формате 'YYYY-MM-DD'
            
        Returns:
            количество дней до дедлайна или None
        """
        if not deadline_str:
            return None
        
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            days = (deadline - date.today()).days
            return days if days >= 0 else None
        except ValueError:
            return None
    
    def calculate_progress_percent(self, current: float, target: float, initial: Optional[float] = None, goal_name: Optional[str] = None) -> float:
        """
        Вычислить процент выполнения цели
        
        Args:
            current: текущее значение
            target: целевое значение
            initial: начальное значение (для целей с уменьшением, например вес)
            goal_name: название цели (для определения направления)
            
        Returns:
            процент выполнения (0-100)
        """
        if target == 0:
            return 0.0
        
        # Для целей с уменьшением (например, вес: от большего к меньшему)
        # Если есть начальное значение и current > target, значит это уменьшение
        if initial is not None and current > target:
            # Прогресс = (initial - current) / (initial - target) * 100
            # Чем меньше current, тем больше прогресс
            if initial == target:
                return 100.0 if current <= target else 0.0
            progress = ((initial - current) / (initial - target)) * 100
            return max(0.0, min(100.0, progress))
        
        # Для обычных целей (увеличение)
        return min(100.0, (current / target) * 100)
    
    def calculate_time_progress(self, deadline_str: Optional[str]) -> Optional[float]:
        """
        Вычислить прогресс по времени (сколько времени прошло до дедлайна)
        
        Args:
            deadline_str: дата дедлайна
            
        Returns:
            процент времени, прошедшего до дедлайна (0-100) или None
        """
        if not deadline_str:
            return None
        
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            start_of_year = date(2026, 1, 1)
            
            total_days = (deadline - start_of_year).days
            passed_days = (date.today() - start_of_year).days
            
            if total_days <= 0:
                return None
            
            progress = (passed_days / total_days) * 100
            return max(0, min(100, progress))
        except ValueError:
            return None
    
    def get_progress_status(self, goal: Dict[str, Any]) -> str:
        """
        Определить статус цели (в графике, опережает, отстает)
        
        Args:
            goal: словарь с данными цели
            
        Returns:
            строка со статусом: 'on_track', 'ahead', 'behind'
        """
        current = goal['current_value']
        target = goal['target_value']
        deadline = goal.get('deadline')
        
        # Получаем начальное значение для расчета прогресса
        initial = goal.get('initial_value')
        goal_name = goal.get('name', '')
        
        # Для целей без дедлайна просто считаем процент
        if not deadline:
            progress = self.calculate_progress_percent(current, target, initial, goal_name)
            if progress >= 100:
                return 'completed'
            elif progress >= 80:
                return 'on_track'
            else:
                return 'behind'
        
        # Для целей с дедлайном сравниваем прогресс по значению и по времени
        value_progress = self.calculate_progress_percent(current, target, initial, goal_name)
        time_progress = self.calculate_time_progress(deadline)
        
        if time_progress is None:
            return 'on_track'
        
        # Если прогресс по значению больше прогресса по времени - опережаем
        if value_progress > time_progress + 10:
            return 'ahead'
        # Если прогресс по значению меньше прогресса по времени - отстаем
        elif value_progress < time_progress - 10:
            return 'behind'
        else:
            return 'on_track'
    
    def format_progress_bar(self, percent: float, length: int = 10) -> str:
        """
        Создать текстовую полосу прогресса
        
        Args:
            percent: процент выполнения (0-100)
            length: длина полосы в символах
            
        Returns:
            строка с полосой прогресса
        """
        filled = int(percent / 100 * length)
        bar = '▓' * filled + '░' * (length - filled)
        return f"{bar} {percent:.0f}%"
    
    def get_today_summary(self, user_id: str) -> str:
        """
        Получить сводку на сегодня
        
        Args:
            user_id: UUID пользователя
        
        Returns:
            форматированная строка со сводкой
        """
        day = self.day_of_year()
        year_progress = round(day / 365 * 100, 1)
        
        msg = f"📅 День {day}/365 ({year_progress}% года прошло)\n\n"
        
        # Получаем все цели пользователя
        goals = self.db.get_user_goals(user_id)
        
        # Группируем по категориям
        categories = {}
        for goal in goals:
            cat = goal['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(goal)
        
        # Ближайшие дедлайны
        upcoming_deadlines = []
        for goal in goals:
            days = self.days_until(goal.get('deadline'))
            if days and 0 < days < 60:
                upcoming_deadlines.append((goal, days))
        
        if upcoming_deadlines:
            msg += "⏰ Ближайшие дедлайны:\n"
            for goal, days in sorted(upcoming_deadlines, key=lambda x: x[1])[:5]:
                msg += f"• {goal['name']}: {days} дней\n"
            msg += "\n"
        
        # Общий прогресс по категориям
        emoji_map = {
            'финансы': '💰',
            'спорт': '🏃',
            'покупки': '🛒',
            'путешествия': '✈️'
        }
        
        msg += "📊 Прогресс по категориям:\n"
        for cat, cat_goals in categories.items():
            emoji = emoji_map.get(cat, '📌')
            total_progress = sum(
                self.calculate_progress_percent(
                    g['current_value'], 
                    g['target_value'],
                    g.get('initial_value'),
                    g.get('name', '')
                )
                for g in cat_goals
            ) / len(cat_goals) if cat_goals else 0
            
            msg += f"{emoji} {cat.capitalize()}: {total_progress:.0f}%\n"
        
        return msg
    
    def get_goals_list(self, user_id: str) -> str:
        """
        Получить список всех целей с их статусом
        
        Args:
            user_id: UUID пользователя
        
        Returns:
            форматированная строка со списком целей
        """
        msg = "📊 МОИ ЦЕЛИ 2026\n\n"
        
        goals = self.db.get_user_goals(user_id)
        categories = {}
        
        for goal in goals:
            cat = goal['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(goal)
        
        emoji_map = {
            'финансы': '💰',
            'спорт': '🏃',
            'покупки': '🛒',
            'путешествия': '✈️'
        }
        
        status_emoji = {
            'on_track': '✅',
            'ahead': '🚀',
            'behind': '⚠️',
            'completed': '🎉'
        }
        
        for cat, cat_goals in categories.items():
            emoji = emoji_map.get(cat, '📌')
            msg += f"{emoji} {cat.upper()}\n"
            
            for goal in cat_goals:
                progress = self.calculate_progress_percent(
                    goal['current_value'], 
                    goal['target_value'],
                    goal.get('initial_value'),
                    goal.get('name', '')
                )
                status = self.get_progress_status(goal)
                status_icon = status_emoji.get(status, '⏳')
                
                # Формируем строку цели
                goal_line = f"├─ {goal['name']}: "
                
                # Для веса показываем начальный → текущий → целевой
                if goal['name'] == 'Вес' and goal.get('initial_value'):
                    initial = goal['initial_value']
                    current = goal['current_value']
                    target = goal['target_value']
                    goal_line += f"{initial:.0f} → {current:.0f} → {target:.0f} {goal['unit']}"
                # Для остальных целей: текущее / целевое
                elif goal['unit']:
                    goal_line += f"{goal['current_value']:.0f}/{goal['target_value']:.0f} {goal['unit']}"
                else:
                    goal_line += f"{goal['current_value']:.0f}/{goal['target_value']:.0f}"
                
                # Дедлайн
                if goal.get('deadline'):
                    days = self.days_until(goal['deadline'])
                    if days is not None:
                        goal_line += f" → {status_icon} Осталось {days} дней"
                
                # Процент выполнения
                goal_line += f" ({progress:.0f}%)\n"
                
                msg += goal_line
            
            msg += "\n"
        
        return msg
    
    def get_weekly_report(self, user_id: str) -> str:
        """
        Получить недельный отчет
        
        Args:
            user_id: UUID пользователя
        
        Returns:
            форматированная строка с отчетом
        """
        msg = "📈 ОТЧЕТ ЗА НЕДЕЛЮ\n\n"
        
        # Получаем отметки за неделю
        checkins = self.db.get_weekly_checkins(user_id)
        
        # Статистика по тренировкам
        workouts_count = sum(1 for c in checkins if c.get('workout'))
        msg += f"🏃 Тренировки: {workouts_count}/7 дней\n"
        
        # Статистика по доходам
        total_income = sum(c.get('income', 0) for c in checkins)
        msg += f"💰 Доход за неделю: {total_income:,.0f} ₽\n\n"
        
        # Прогресс по целям
        goals = self.db.get_user_goals(user_id)
        
        msg += "📊 Прогресс по целям:\n"
        for goal in goals[:5]:  # Показываем первые 5 целей
            progress = self.calculate_progress_percent(
                goal['current_value'],
                goal['target_value'],
                goal.get('initial_value'),
                goal.get('name', '')
            )
            bar = self.format_progress_bar(progress)
            msg += f"• {goal['name']}: {bar}\n"
        
        return msg

