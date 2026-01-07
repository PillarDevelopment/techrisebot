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
from database_supabase import SupabaseDatabase
from goals import GoalsCalculator

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Класс для управления уведомлениями для множественных пользователей"""
    
    def __init__(self, bot, db: SupabaseDatabase):
        """
        Инициализация планировщика
        
        Args:
            bot: объект бота Telegram
            db: объект базы данных Supabase
        """
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.calculator = GoalsCalculator(self.db)
        self.tz = timezone(TIMEZONE)
    
    async def send_morning_notification(self):
        """Отправить утреннее уведомление в 9:00 всем пользователям с включенными уведомлениями"""
        try:
            # Получаем всех пользователей с включенными уведомлениями
            users = self.db.get_users_with_notifications_enabled()
            
            if not users:
                logger.info("Нет пользователей с включенными уведомлениями")
                return
            
            day = self.calculator.day_of_year()
            
            # Отправляем уведомления каждому пользователю
            for user in users:
                try:
                    user_id = user['id']
                    telegram_user_id = user['telegram_user_id']
                    
                    # Проверяем, включены ли уведомления для этого пользователя
                    notifications_enabled = self.db.get_setting(user_id, 'notifications_enabled', 'on')
                    if notifications_enabled != 'on':
                        continue
                    
                    msg = f"☀️ Доброе утро! День {day}/365\n\n"
                    msg += "🎯 Фокус на сегодня:\n"
                    
                    # Получаем цели пользователя с ближайшими дедлайнами
                    goals = self.db.get_user_goals(user_id)
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
                    
                    await self.bot.send_message(chat_id=telegram_user_id, text=msg)
                    logger.info(f"Отправлено утреннее уведомление пользователю {telegram_user_id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при отправке утреннего уведомления пользователю {user.get('telegram_user_id')}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Ошибка при отправке утренних уведомлений: {e}")
    
    async def send_evening_notification(self):
        """Отправить вечернее уведомление в 21:00 всем пользователям с включенными уведомлениями"""
        try:
            # Получаем всех пользователей с включенными уведомлениями
            users = self.db.get_users_with_notifications_enabled()
            
            if not users:
                logger.info("Нет пользователей с включенными уведомлениями")
                return
            
            # Отправляем уведомления каждому пользователю
            for user in users:
                try:
                    user_id = user['id']
                    telegram_user_id = user['telegram_user_id']
                    
                    # Проверяем, включены ли уведомления для этого пользователя
                    notifications_enabled = self.db.get_setting(user_id, 'notifications_enabled', 'on')
                    if notifications_enabled != 'on':
                        continue
                    
                    msg = "🌙 Как прошел день?\n\n"
                    msg += "Ответь на вопросы:\n"
                    msg += "1. Была ли тренировка? (да/нет или /update тренировка да)\n"
                    msg += "2. Сколько заработал сегодня? (/update доход [число])\n"
                    msg += "3. Новые знакомства? (/update знакомства [число])\n\n"
                    msg += "Или напиши /skip чтобы пропустить"
                    
                    await self.bot.send_message(chat_id=telegram_user_id, text=msg)
                    logger.info(f"Отправлено вечернее уведомление пользователю {telegram_user_id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при отправке вечернего уведомления пользователю {user.get('telegram_user_id')}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Ошибка при отправке вечерних уведомлений: {e}")
    
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

