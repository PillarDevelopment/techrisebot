"""
Тестовый скрипт для проверки работы модуля database_supabase.py

Использование:
    python3 test_database_supabase.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_database_module():
    """Тестирование модуля database_supabase"""
    
    print("=" * 60)
    print("Тест модуля database_supabase.py")
    print("=" * 60)
    print()
    
    try:
        from database_supabase import SupabaseDatabase
        
        print("✅ Модуль database_supabase импортирован")
        
        # Создаем экземпляр класса
        db = SupabaseDatabase()
        print("✅ Экземпляр SupabaseDatabase создан")
        
        # Тест 1: Создание/получение пользователя
        print("\n📝 Тест 1: Создание/получение пользователя")
        telegram_data = {
            'id': 123456789,
            'first_name': 'Тестовый',
            'last_name': 'Пользователь',
            'username': 'test_user',
            'language_code': 'ru'
        }
        
        user = db.get_or_create_user(123456789, telegram_data)
        print(f"✅ Пользователь создан/найден: {user['id']}")
        print(f"   Имя: {user['first_name']} {user.get('last_name', '')}")
        print(f"   Telegram ID: {user['telegram_user_id']}")
        
        user_id = user['id']
        
        # Тест 2: Инициализация дефолтных целей
        print("\n📝 Тест 2: Инициализация дефолтных целей")
        goals = db.init_default_goals(user_id)
        print(f"✅ Создано {len(goals)} дефолтных целей")
        
        # Тест 3: Получение целей пользователя
        print("\n📝 Тест 3: Получение целей пользователя")
        user_goals = db.get_user_goals(user_id)
        print(f"✅ Получено {len(user_goals)} целей")
        
        # Показываем первые 3 цели
        for i, goal in enumerate(user_goals[:3], 1):
            print(f"   {i}. {goal['category']} - {goal['name']}: {goal['current_value']}/{goal['target_value']}")
        
        # Тест 4: Обновление цели
        if len(user_goals) > 0:
            print("\n📝 Тест 4: Обновление цели")
            test_goal = user_goals[0]
            updated_goal = db.update_goal_value(
                user_id=user_id,
                goal_id=test_goal['id'],
                new_value=test_goal['current_value'] + 1,
                note='Тестовое обновление'
            )
            print(f"✅ Цель обновлена: {updated_goal['name']} = {updated_goal['current_value']}")
        
        # Тест 5: Получение настроек
        print("\n📝 Тест 5: Работа с настройками")
        setting = db.set_setting(user_id, 'notifications_enabled', 'on')
        print(f"✅ Настройка установлена: notifications_enabled = on")
        
        value = db.get_setting(user_id, 'notifications_enabled', 'off')
        print(f"✅ Настройка получена: notifications_enabled = {value}")
        
        # Тест 6: Добавление ежедневной отметки
        print("\n📝 Тест 6: Добавление ежедневной отметки")
        checkin = db.add_daily_checkin(
            user_id=user_id,
            workout=True,
            income=50000.0,
            weight=85.0,
            notes='Тестовая отметка'
        )
        print(f"✅ Ежедневная отметка добавлена за {checkin['date']}")
        
        print("\n" + "=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_database_module()
    exit(0 if success else 1)

