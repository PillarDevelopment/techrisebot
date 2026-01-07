"""
Тестовый скрипт для проверки подключения к Supabase.

Использование:
    python3 test_supabase_connection.py

Перед запуском убедитесь, что в .env файле указаны:
    SUPABASE_URL=https://xxx.supabase.co
    SUPABASE_KEY=eyJ...
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_supabase_connection():
    """Проверка подключения к Supabase"""
    
    # Проверяем наличие переменных окружения
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url:
        print("❌ Ошибка: SUPABASE_URL не найден в .env")
        return False
    
    if not supabase_key:
        print("❌ Ошибка: SUPABASE_KEY не найден в .env")
        return False
    
    print(f"✅ SUPABASE_URL найден: {supabase_url[:30]}...")
    print(f"✅ SUPABASE_KEY найден: {supabase_key[:20]}...")
    
    try:
        # Пытаемся импортировать supabase
        from supabase import create_client, Client
        
        print("✅ Модуль supabase-py установлен")
        
        # Создаем клиент
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Клиент Supabase создан")
        
        # Пытаемся выполнить простой запрос
        # Проверяем доступность API через health check или простой запрос
        try:
            # Простой способ проверить подключение - попробовать получить список таблиц
            # Или выполнить простой SELECT запрос через RPC
            response = supabase.table('users').select('id').limit(1).execute()
            print("✅ Подключение к Supabase работает!")
            print(f"✅ Успешный запрос к таблице 'users'")
            return True
        except Exception as e:
            # Если таблицы еще нет - это нормально на этапе настройки
            error_str = str(e)
            if ("relation" in error_str.lower() or 
                "does not exist" in error_str.lower() or 
                "PGRST205" in error_str or
                "table" in error_str.lower() and "not found" in error_str.lower()):
                print("⚠️  Таблицы еще не созданы, но подключение работает")
                print("   Это нормально на этапе настройки схемы БД")
                print("   Выполните миграции из папки migrations/")
                return True
            else:
                print(f"❌ Ошибка при выполнении запроса: {e}")
                return False
                
    except ImportError:
        print("❌ Ошибка: Модуль supabase-py не установлен")
        print("   Установите: pip install supabase-py")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Тест подключения к Supabase")
    print("=" * 50)
    print()
    
    success = test_supabase_connection()
    
    print()
    print("=" * 50)
    if success:
        print("✅ Все проверки пройдены!")
    else:
        print("❌ Обнаружены проблемы. Проверьте настройки.")
    print("=" * 50)

