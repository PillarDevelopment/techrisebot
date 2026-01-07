"""
Модуль для работы с базой данных Supabase (PostgreSQL).
Здесь выполняются операции с данными через Supabase API.
"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Импортируем supabase с обработкой ошибок версий
try:
    from supabase import create_client, Client
except ImportError as e:
    logger.error(f"Не удалось импортировать supabase: {e}")
    raise


class SupabaseDatabase:
    """Класс для работы с базой данных Supabase"""
    
    def __init__(self):
        """
        Инициализация подключения к Supabase
        
        Raises:
            ValueError: Если SUPABASE_URL или SUPABASE_KEY не установлены
        """
        if not SUPABASE_URL:
            raise ValueError("SUPABASE_URL не установлен в переменных окружения")
        if not SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY не установлен в переменных окружения")
        
        try:
            # Создаем клиент - используем позиционные аргументы для максимальной совместимости
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Подключение к Supabase установлено")
        except TypeError as e:
            error_msg = str(e)
            # Если ошибка связана с proxy или другими неожиданными аргументами
            if "unexpected keyword argument" in error_msg or "proxy" in error_msg.lower():
                logger.error(f"Ошибка версии библиотеки supabase-py: {e}")
                logger.error("Попробуйте обновить библиотеку: pip install --upgrade supabase")
                raise ValueError(
                    f"Несовместимость версий библиотеки supabase-py. "
                    f"Ошибка: {e}. "
                    f"Попробуйте: pip install --upgrade supabase httpx"
                )
            else:
                logger.error(f"Ошибка подключения к Supabase: {e}")
                raise
        except Exception as e:
            logger.error(f"Ошибка подключения к Supabase: {e}")
            raise
    
    # ========================================================================
    # МЕТОДЫ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
    # ========================================================================
    
    def get_or_create_user(self, telegram_user_id: int, telegram_data: dict) -> dict:
        """
        Получить существующего пользователя или создать нового
        
        Args:
            telegram_user_id: Telegram User ID
            telegram_data: Данные из update.message.from:
                {
                    'id': 123456789,
                    'first_name': 'Иван',
                    'last_name': 'Иванов',
                    'username': 'ivan_user',
                    'language_code': 'ru'
                }
        
        Returns:
            dict: Данные пользователя с полем 'id' (UUID)
        
        Raises:
            Exception: Ошибка при работе с БД
        """
        try:
            # Пытаемся найти существующего пользователя
            response = self.client.table('users')\
                .select('*')\
                .eq('telegram_user_id', telegram_user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Пользователь найден: telegram_user_id={telegram_user_id}")
                return response.data[0]
            
            # Пользователь не найден - создаем нового
            new_user = {
                'telegram_user_id': telegram_user_id,
                'telegram_username': telegram_data.get('username'),
                'first_name': telegram_data.get('first_name'),
                'last_name': telegram_data.get('last_name'),
                'language_code': telegram_data.get('language_code', 'ru'),
                'is_active': True
            }
            
            response = self.client.table('users')\
                .insert(new_user)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Создан новый пользователь: telegram_user_id={telegram_user_id}, id={response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("Не удалось создать пользователя")
                
        except Exception as e:
            logger.error(f"Ошибка в get_or_create_user: {e}")
            raise
    
    def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[dict]:
        """
        Получить пользователя по Telegram User ID
        
        Args:
            telegram_user_id: Telegram User ID
        
        Returns:
            dict: Данные пользователя или None если не найден
        """
        try:
            response = self.client.table('users')\
                .select('*')\
                .eq('telegram_user_id', telegram_user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка в get_user_by_telegram_id: {e}")
            return None
    
    def update_user(self, user_id: str, **kwargs) -> dict:
        """
        Обновить данные пользователя
        
        Args:
            user_id: UUID пользователя
            **kwargs: Поля для обновления (first_name, last_name, telegram_username, language_code, is_active)
        
        Returns:
            dict: Обновленные данные пользователя
        """
        try:
            response = self.client.table('users')\
                .update(kwargs)\
                .eq('id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Обновлен пользователь: id={user_id}")
                return response.data[0]
            else:
                raise Exception(f"Пользователь с id={user_id} не найден")
                
        except Exception as e:
            logger.error(f"Ошибка в update_user: {e}")
            raise
    
    def get_users_with_notifications_enabled(self) -> List[Dict[str, Any]]:
        """
        Получить список всех пользователей с включенными уведомлениями
        
        Returns:
            list: Список пользователей с включенными уведомлениями
        """
        try:
            # Получаем всех активных пользователей
            users_response = self.client.table('users')\
                .select('id, telegram_user_id, first_name, last_name')\
                .eq('is_active', True)\
                .execute()
            
            if not users_response.data:
                return []
            
            # Фильтруем пользователей с включенными уведомлениями
            users_with_notifications = []
            for user in users_response.data:
                user_id = user['id']
                # Проверяем настройку уведомлений (по умолчанию 'on')
                setting = self.get_setting(user_id, 'notifications_enabled', 'on')
                if setting == 'on':
                    users_with_notifications.append(user)
            
            return users_with_notifications
            
        except Exception as e:
            logger.error(f"Ошибка в get_users_with_notifications_enabled: {e}")
            return []
    
    # ========================================================================
    # МЕТОДЫ РАБОТЫ С ЦЕЛЯМИ
    # ========================================================================
    
    def get_user_goals(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить цели пользователя
        
        Args:
            user_id: UUID пользователя
            category: Фильтр по категории (опционально)
        
        Returns:
            list: Список целей пользователя
        """
        try:
            query = self.client.table('goals')\
                .select('*')\
                .eq('user_id', user_id)
            
            if category:
                query = query.eq('category', category)
            
            query = query.order('deadline', desc=False)\
                .order('category', desc=False)\
                .execute()
            
            return query.data if query.data else []
            
        except Exception as e:
            logger.error(f"Ошибка в get_user_goals: {e}")
            return []
    
    def get_goal_by_id(self, user_id: str, goal_id: str) -> Optional[dict]:
        """
        Получить конкретную цель пользователя
        
        Args:
            user_id: UUID пользователя (для проверки принадлежности)
            goal_id: UUID цели
        
        Returns:
            dict: Данные цели или None если не найдена
        """
        try:
            response = self.client.table('goals')\
                .select('*')\
                .eq('id', goal_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка в get_goal_by_id: {e}")
            return None
    
    def create_goal(self, user_id: str, category: str, name: str, target_value: float,
                    initial_value: Optional[float] = None, unit: Optional[str] = None,
                    deadline: Optional[str] = None) -> dict:
        """
        Создать новую цель для пользователя
        
        Args:
            user_id: UUID пользователя
            category: Категория цели
            name: Название цели
            target_value: Целевое значение
            initial_value: Начальное значение (для веса)
            unit: Единица измерения
            deadline: Дата дедлайна (YYYY-MM-DD)
        
        Returns:
            dict: Созданная цель
        """
        try:
            goal_data = {
                'user_id': user_id,
                'category': category,
                'name': name,
                'target_value': target_value,
                'current_value': 0,
                'unit': unit,
                'deadline': deadline
            }
            
            if initial_value is not None:
                goal_data['initial_value'] = initial_value
            
            response = self.client.table('goals')\
                .insert(goal_data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Создана цель: user_id={user_id}, name={name}")
                return response.data[0]
            else:
                raise Exception("Не удалось создать цель")
                
        except Exception as e:
            logger.error(f"Ошибка в create_goal: {e}")
            raise
    
    def update_goal_value(self, user_id: str, goal_id: str, new_value: float, note: Optional[str] = None) -> dict:
        """
        Обновить значение цели
        
        Args:
            user_id: UUID пользователя (для проверки принадлежности)
            goal_id: UUID цели
            new_value: Новое значение
            note: Примечание к обновлению
        
        Returns:
            dict: Обновленная цель
        """
        try:
            # Проверяем принадлежность цели пользователю
            goal = self.get_goal_by_id(user_id, goal_id)
            if not goal:
                raise ValueError(f"Цель {goal_id} не найдена или не принадлежит пользователю {user_id}")
            
            # Обновляем значение цели
            response = self.client.table('goals')\
                .update({'current_value': new_value})\
                .eq('id', goal_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Не удалось обновить цель")
            
            updated_goal = response.data[0]
            
            # Создаем запись в истории прогресса
            self.add_progress_log(user_id, goal_id, new_value, note)
            
            logger.info(f"Обновлена цель: goal_id={goal_id}, new_value={new_value}")
            return updated_goal
            
        except Exception as e:
            logger.error(f"Ошибка в update_goal_value: {e}")
            raise
    
    def update_goal_by_name(self, user_id: str, category: str, name: str, value: float) -> dict:
        """
        Обновить цель по категории и названию
        
        Args:
            user_id: UUID пользователя
            category: Категория цели
            name: Название цели
            value: Новое значение
        
        Returns:
            dict: Обновленная цель
        """
        try:
            # Находим цель
            goals = self.get_user_goals(user_id, category)
            goal = None
            for g in goals:
                if g['name'] == name:
                    goal = g
                    break
            
            if not goal:
                raise ValueError(f"Цель '{name}' в категории '{category}' не найдена")
            
            return self.update_goal_value(user_id, goal['id'], value)
            
        except Exception as e:
            logger.error(f"Ошибка в update_goal_by_name: {e}")
            raise
    
    def delete_goal(self, user_id: str, goal_id: str) -> bool:
        """
        Удалить цель пользователя
        
        Args:
            user_id: UUID пользователя (для проверки принадлежности)
            goal_id: UUID цели
        
        Returns:
            bool: True если удалено, False если не найдено
        """
        try:
            # Проверяем принадлежность
            goal = self.get_goal_by_id(user_id, goal_id)
            if not goal:
                return False
            
            # Удаляем цель (каскадное удаление прогресса произойдет автоматически)
            self.client.table('goals')\
                .delete()\
                .eq('id', goal_id)\
                .eq('user_id', user_id)\
                .execute()
            
            logger.info(f"Удалена цель: goal_id={goal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка в delete_goal: {e}")
            return False
    
    # ========================================================================
    # МЕТОДЫ РАБОТЫ С ИСТОРИЕЙ ПРОГРЕССА
    # ========================================================================
    
    def add_progress_log(self, user_id: str, goal_id: str, value: float, note: Optional[str] = None) -> dict:
        """
        Добавить запись в историю прогресса
        
        Args:
            user_id: UUID пользователя
            goal_id: UUID цели
            value: Значение
            note: Примечание
        
        Returns:
            dict: Созданная запись
        """
        try:
            log_data = {
                'user_id': user_id,
                'goal_id': goal_id,
                'value': value,
                'note': note
            }
            
            response = self.client.table('progress_log')\
                .insert(log_data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("Не удалось создать запись в истории")
                
        except Exception as e:
            logger.error(f"Ошибка в add_progress_log: {e}")
            raise
    
    def get_progress_history(self, user_id: str, goal_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        """
        Получить историю прогресса пользователя
        
        Args:
            user_id: UUID пользователя
            goal_id: Фильтр по цели (опционально)
            limit: Максимальное количество записей
        
        Returns:
            list: Список записей истории
        """
        try:
            query = self.client.table('progress_log')\
                .select('*')\
                .eq('user_id', user_id)
            
            if goal_id:
                query = query.eq('goal_id', goal_id)
            
            query = query.order('logged_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return query.data if query.data else []
            
        except Exception as e:
            logger.error(f"Ошибка в get_progress_history: {e}")
            return []
    
    # ========================================================================
    # МЕТОДЫ РАБОТЫ С ЕЖЕДНЕВНЫМИ ОТМЕТКАМИ
    # ========================================================================
    
    def add_daily_checkin(self, user_id: str, date_str: Optional[str] = None, workout: bool = False,
                         income: float = 0, new_connections: int = 0, weight: Optional[float] = None,
                         notes: Optional[str] = None) -> dict:
        """
        Добавить ежедневную отметку
        
        Args:
            user_id: UUID пользователя
            date_str: Дата (YYYY-MM-DD), по умолчанию сегодня
            workout: Была ли тренировка
            income: Доход за день
            new_connections: Количество новых знакомств
            weight: Вес
            notes: Заметки
        
        Returns:
            dict: Созданная отметка
        """
        try:
            if not date_str:
                date_str = date.today().isoformat()
            
            checkin_data = {
                'user_id': user_id,
                'date': date_str,
                'workout': workout,
                'income': income,
                'new_connections': new_connections,
                'notes': notes
            }
            
            if weight is not None:
                checkin_data['weight'] = weight
            
            # Используем upsert для обновления существующей записи или создания новой
            response = self.client.table('daily_checkins')\
                .upsert(checkin_data, on_conflict='user_id,date')\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Добавлена отметка: user_id={user_id}, date={date_str}")
                return response.data[0]
            else:
                raise Exception("Не удалось создать отметку")
                
        except Exception as e:
            logger.error(f"Ошибка в add_daily_checkin: {e}")
            raise
    
    def get_daily_checkin(self, user_id: str, date_str: Optional[str] = None) -> Optional[dict]:
        """
        Получить ежедневную отметку за конкретную дату
        
        Args:
            user_id: UUID пользователя
            date_str: Дата (YYYY-MM-DD), по умолчанию сегодня
        
        Returns:
            dict: Данные отметки или None
        """
        try:
            if not date_str:
                date_str = date.today().isoformat()
            
            response = self.client.table('daily_checkins')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('date', date_str)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Ошибка в get_daily_checkin: {e}")
            return None
    
    def get_weekly_checkins(self, user_id: str) -> List[dict]:
        """
        Получить отметки за последние 7 дней
        
        Args:
            user_id: UUID пользователя
        
        Returns:
            list: Список отметок за неделю
        """
        try:
            # Получаем отметки за последние 7 дней
            seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
            
            response = self.client.table('daily_checkins')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('date', seven_days_ago)\
                .order('date', desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Ошибка в get_weekly_checkins: {e}")
            return []
    
    # ========================================================================
    # МЕТОДЫ РАБОТЫ С НАСТРОЙКАМИ
    # ========================================================================
    
    def get_setting(self, user_id: str, key: str, default: str = '') -> str:
        """
        Получить настройку пользователя
        
        Args:
            user_id: UUID пользователя
            key: Ключ настройки
            default: Значение по умолчанию
        
        Returns:
            str: Значение настройки
        """
        try:
            response = self.client.table('settings')\
                .select('value')\
                .eq('user_id', user_id)\
                .eq('key', key)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get('value', default)
            return default
            
        except Exception as e:
            logger.error(f"Ошибка в get_setting: {e}")
            return default
    
    def set_setting(self, user_id: str, key: str, value: str) -> dict:
        """
        Установить настройку пользователя
        
        Args:
            user_id: UUID пользователя
            key: Ключ настройки
            value: Значение настройки
        
        Returns:
            dict: Обновленная настройка
        """
        try:
            setting_data = {
                'user_id': user_id,
                'key': key,
                'value': value
            }
            
            # Используем upsert для обновления существующей настройки или создания новой
            response = self.client.table('settings')\
                .upsert(setting_data, on_conflict='user_id,key')\
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Установлена настройка: user_id={user_id}, key={key}")
                return response.data[0]
            else:
                raise Exception("Не удалось установить настройку")
                
        except Exception as e:
            logger.error(f"Ошибка в set_setting: {e}")
            raise
    
    # ========================================================================
    # МЕТОДЫ ИНИЦИАЛИЗАЦИИ
    # ========================================================================
    
    def init_default_goals(self, user_id: str) -> List[dict]:
        """
        Инициализировать дефолтные цели для нового пользователя
        
        ВАЖНО: Каждый пользователь получает свои собственные цели с его user_id!
        
        Args:
            user_id: UUID пользователя
        
        Returns:
            list: Список созданных целей
        """
        try:
            # Проверяем, есть ли уже цели у пользователя
            existing_goals = self.get_user_goals(user_id)
            if len(existing_goals) > 0:
                logger.info(f"У пользователя {user_id} уже есть цели, пропускаем инициализацию")
                return existing_goals
            
            # Дефолтные цели (шаблон)
            default_goals = [
                # Финансы
                {'category': 'финансы', 'name': 'Доход 1М/мес', 'target_value': 1000000,
                 'current_value': 0, 'unit': '₽/мес', 'deadline': '2026-02-28'},
                {'category': 'финансы', 'name': 'Доход 2М/мес', 'target_value': 2000000,
                 'current_value': 0, 'unit': '₽/мес', 'deadline': '2026-05-31'},
                {'category': 'финансы', 'name': 'Доход 5М/мес', 'target_value': 5000000,
                 'current_value': 0, 'unit': '₽/мес', 'deadline': '2026-11-30'},
                {'category': 'финансы', 'name': 'Источники дохода', 'target_value': 4,
                 'current_value': 0, 'unit': 'шт', 'deadline': '2026-06-30'},
                
                # Спорт и здоровье
                {'category': 'спорт', 'name': 'Вес', 'target_value': 80, 'current_value': 87,
                 'initial_value': 105, 'unit': 'кг', 'deadline': '2026-06-30'},
                {'category': 'спорт', 'name': 'Тренировки в неделю', 'target_value': 4,
                 'current_value': 0, 'unit': 'шт/нед', 'deadline': None},
                {'category': 'спорт', 'name': 'Марафоны', 'target_value': 2,
                 'current_value': 0, 'unit': 'шт', 'deadline': '2026-09-30'},
                
                # Покупки
                {'category': 'покупки', 'name': 'Voyah Free (авто)', 'target_value': 1,
                 'current_value': 0, 'unit': 'шт', 'deadline': '2026-06-30'},
                {'category': 'покупки', 'name': 'Квартира в Москве', 'target_value': 25000000,
                 'current_value': 0, 'unit': '₽', 'deadline': '2026-06-30'},
                
                # Путешествия
                {'category': 'путешествия', 'name': 'Новые страны', 'target_value': 12,
                 'current_value': 0, 'unit': 'шт', 'deadline': '2026-12-31'},
            ]
            
            created_goals = []
            for goal_data in default_goals:
                try:
                    goal = self.create_goal(
                        user_id=user_id,
                        category=goal_data['category'],
                        name=goal_data['name'],
                        target_value=goal_data['target_value'],
                        initial_value=goal_data.get('initial_value'),
                        unit=goal_data.get('unit'),
                        deadline=goal_data.get('deadline')
                    )
                    created_goals.append(goal)
                except Exception as e:
                    logger.warning(f"Не удалось создать цель {goal_data['name']}: {e}")
                    # Продолжаем создание остальных целей
            
            logger.info(f"Создано {len(created_goals)} дефолтных целей для пользователя {user_id}")
            return created_goals
            
        except Exception as e:
            logger.error(f"Ошибка в init_default_goals: {e}")
            raise

