"""
Модуль для планирования уведомлений.
Здесь настраиваются ежедневные напоминания в 9:00 и 21:00 МСК.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from config import TIMEZONE, MORNING_HOUR, MORNING_MINUTE, EVENING_HOUR, EVENING_MINUTE
from database import Database
from goals import GoalsCalculator

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Класс для управления уведомлениями"""
    
    def __init__(self, bot, user_id: int):
        """
        Инициализация планировщика
        
        Args:
            bot: объект бота Telegram
            user_id: ID пользователя для отправки уведомлений
        """
        self.bot = bot
        self.user_id = user_id
        self.scheduler = AsyncIOScheduler()
        self.db = Database()
        self.calculator = GoalsCalculator(self.db)
        self.tz = timezone(TIMEZONE)
    
    async def send_morning_notification(self):
        """Отправить утреннее уведомление в 9:00"""
        try:
            # Проверяем, включены ли уведомления
            notifications_enabled = self.db.get_setting('notifications_enabled', 'on')
            if notifications_enabled != 'on':
                logger.info("Уведомления выключены, пропускаем утреннее уведомление")
                return
            
            day = self.calculator.day_of_year()
            msg = f"☀️ Доброе утро! День {day}/365\n\n"
            msg += "🎯 Фокус на сегодня:\n"
            
            # Получаем цели с ближайшими дедлайнами
            goals = self.db.get_goals_by_category()
            upcoming = []
            
            for goal in goals:
                days = self.calculator.days_until(goal.get('deadline'))
                if days and 0 < days < 30:
                    upcoming.append((goal, days))
            
            if upcoming:
                for goal, days in sorted(upcoming, key=lambda x: x[1])[:3]:
                    msg += f"• До дедлайна \"{goal['name']}\" осталось {days} дней\n"
            
            # Статус по категориям
            categories = {}
            for goal in goals:
                cat = goal['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(goal)
            
            on_track = []
            need_speed = []
            
            for cat, cat_goals in categories.items():
                all_on_track = True
                for goal in cat_goals:
                    status = self.calculator.get_progress_status(goal)
                    if status == 'behind':
                        all_on_track = False
                        break
                
                if all_on_track:
                    on_track.append(cat)
                else:
                    need_speed.append(cat)
            
            if on_track:
                emoji_map = {'финансы': '💰', 'спорт': '🏃', 'покупки': '🛒', 'путешествия': '✈️'}
                on_track_str = ', '.join([emoji_map.get(c, c) for c in on_track])
                msg += f"\n💪 Ты в графике по: {on_track_str}\n"
            
            if need_speed:
                emoji_map = {'финансы': '💰', 'спорт': '🏃', 'покупки': '🛒', 'путешествия': '✈️'}
                need_speed_str = ', '.join([emoji_map.get(c, c) for c in need_speed])
                msg += f"⚠️ Нужно ускориться: {need_speed_str}\n"
            
            msg += "\nХорошего дня! 💪"
            
            await self.bot.send_message(chat_id=self.user_id, text=msg)
            logger.info("Отправлено утреннее уведомление")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке утреннего уведомления: {e}")
    
    async def send_evening_notification(self):
        """Отправить вечернее уведомление в 21:00"""
        try:
            # Проверяем, включены ли уведомления
            notifications_enabled = self.db.get_setting('notifications_enabled', 'on')
            if notifications_enabled != 'on':
                logger.info("Уведомления выключены, пропускаем вечернее уведомление")
                return
            
            msg = "🌙 Как прошел день?\n\n"
            msg += "Ответь на вопросы:\n"
            msg += "1. Была ли тренировка? (да/нет или /update тренировка да)\n"
            msg += "2. Сколько заработал сегодня? (/update доход [число])\n"
            msg += "3. Новые знакомства? (/update знакомства [число])\n\n"
            msg += "Или напиши /skip чтобы пропустить"
            
            await self.bot.send_message(chat_id=self.user_id, text=msg)
            logger.info("Отправлено вечернее уведомление")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке вечернего уведомления: {e}")
    
    def start(self):
        """Запустить планировщик уведомлений"""
        # Утреннее уведомление в 9:00 МСК
        self.scheduler.add_job(
            self.send_morning_notification,
            trigger=CronTrigger(hour=MORNING_HOUR, minute=MORNING_MINUTE, timezone=self.tz),
            id='morning_notification',
            replace_existing=True
        )
        
        # Вечернее уведомление в 21:00 МСК
        self.scheduler.add_job(
            self.send_evening_notification,
            trigger=CronTrigger(hour=EVENING_HOUR, minute=EVENING_MINUTE, timezone=self.tz),
            id='evening_notification',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Планировщик уведомлений запущен")
    
    def stop(self):
        """Остановить планировщик"""
        self.scheduler.shutdown()
        logger.info("Планировщик уведомлений остановлен")

