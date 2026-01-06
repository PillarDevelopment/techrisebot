"""
Модуль для работы с базой данных SQLite.
Здесь создаются таблицы и выполняются операции с данными.
"""
import sqlite3
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from config import DATABASE_NAME

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        """
        Инициализация подключения к базе данных
        
        Args:
            db_name: имя файла базы данных
        """
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Получить подключение к базе данных
        
        Returns:
            объект подключения к SQLite
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Возвращает результаты как словари
        return conn
    
    def init_database(self):
        """Создать таблицы в базе данных, если их еще нет"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица целей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                unit TEXT,
                deadline DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, name)
            )
        ''')
        
        # Таблица логов прогресса
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER,
                value REAL,
                note TEXT,
                logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        ''')
        
        # Таблица ежедневных отметок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                workout BOOLEAN DEFAULT 0,
                income REAL DEFAULT 0,
                new_connections INTEGER DEFAULT 0,
                weight REAL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица настроек уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    
    def init_default_goals(self):
        """Инициализировать цели по умолчанию из ТЗ"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже цели
        cursor.execute('SELECT COUNT(*) FROM goals')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Финансовые цели
        goals_data = [
            ('финансы', 'Доход 1М/мес', 1000000, 0, '₽/мес', '2026-02-28'),
            ('финансы', 'Доход 2М/мес', 2000000, 0, '₽/мес', '2026-05-31'),
            ('финансы', 'Доход 5М/мес', 5000000, 0, '₽/мес', '2026-11-30'),
            ('финансы', 'Источники дохода', 4, 0, 'шт', '2026-06-30'),
            
            # Спорт и здоровье
            ('спорт', 'Вес', 80, 87, 'кг', '2026-06-30'),
            ('спорт', 'Тренировки в неделю', 4, 0, 'шт/нед', None),
            ('спорт', 'Марафоны', 2, 0, 'шт', '2026-09-30'),
            
            # Покупки
            ('покупки', 'Voyah Free (авто)', 1, 0, 'шт', '2026-06-30'),
            ('покупки', 'Квартира в Москве', 25000000, 0, '₽', '2026-06-30'),
            
            # Путешествия
            ('путешествия', 'Новые страны', 12, 0, 'шт', '2026-12-31'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO goals (category, name, target_value, current_value, unit, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', goals_data)
        
        conn.commit()
        conn.close()
        logger.info("Цели по умолчанию добавлены")
    
    def get_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить цель по ID
        
        Args:
            goal_id: ID цели
            
        Returns:
            словарь с данными цели или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM goals WHERE id = ?', (goal_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_goals_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Получить все цели или цели по категории
        
        Args:
            category: категория цели (финансы, спорт, покупки, путешествия)
            
        Returns:
            список словарей с данными целей
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM goals WHERE category = ? ORDER BY deadline', (category,))
        else:
            cursor.execute('SELECT * FROM goals ORDER BY category, deadline')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_goal_value(self, goal_id: int, new_value: float, note: Optional[str] = None):
        """
        Обновить текущее значение цели
        
        Args:
            goal_id: ID цели
            new_value: новое значение
            note: примечание к обновлению
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Обновляем значение цели
        cursor.execute('''
            UPDATE goals 
            SET current_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_value, goal_id))
        
        # Добавляем запись в лог
        cursor.execute('''
            INSERT INTO progress_log (goal_id, value, note)
            VALUES (?, ?, ?)
        ''', (goal_id, new_value, note))
        
        conn.commit()
        conn.close()
        logger.info(f"Обновлена цель {goal_id}: новое значение {new_value}")
    
    def update_goal_by_name(self, category: str, name: str, value: float):
        """
        Обновить цель по категории и названию
        
        Args:
            category: категория цели
            name: название цели
            value: новое значение
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Находим цель
        cursor.execute('SELECT id FROM goals WHERE category = ? AND name = ?', (category, name))
        goal = cursor.fetchone()
        conn.close()
        
        if goal:
            self.update_goal_value(goal['id'], value)
        else:
            logger.warning(f"Цель не найдена: {category} - {name}")
    
    def add_daily_checkin(self, workout: bool = False, income: float = 0, 
                         new_connections: int = 0, weight: Optional[float] = None, 
                         notes: Optional[str] = None):
        """
        Добавить ежедневную отметку
        
        Args:
            workout: была ли тренировка
            income: доход за день
            new_connections: количество новых знакомств
            weight: текущий вес
            notes: заметки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_checkins 
            (date, workout, income, new_connections, weight, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (today, workout, income, new_connections, weight, notes))
        
        conn.commit()
        conn.close()
        logger.info(f"Добавлена отметка за {today}")
    
    def get_weekly_checkins(self) -> List[Dict[str, Any]]:
        """
        Получить отметки за текущую неделю
        
        Returns:
            список словарей с данными отметок
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем отметки за последние 7 дней
        cursor.execute('''
            SELECT * FROM daily_checkins 
            WHERE date >= date('now', '-7 days')
            ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_setting(self, key: str, default: str = '') -> str:
        """
        Получить настройку
        
        Args:
            key: ключ настройки
            default: значение по умолчанию
            
        Returns:
            значение настройки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default
    
    def set_setting(self, key: str, value: str):
        """
        Установить настройку
        
        Args:
            key: ключ настройки
            value: значение настройки
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()

