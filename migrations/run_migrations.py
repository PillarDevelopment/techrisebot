"""
Скрипт для выполнения миграций базы данных Supabase.

Использование:
    python3 migrations/run_migrations.py

Требования:
    - Установлен supabase-py: pip install supabase
    - Настроены переменные окружения в .env:
      SUPABASE_URL
      SUPABASE_SERVICE_ROLE_KEY
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

def run_migrations():
    """Выполнить все миграции базы данных"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url:
        print("❌ Ошибка: SUPABASE_URL не найден в .env")
        return False
    
    if not supabase_service_key:
        print("❌ Ошибка: SUPABASE_SERVICE_ROLE_KEY не найден в .env")
        print("   Используйте Service Role Key для выполнения миграций")
        return False
    
    try:
        from supabase import create_client
        
        supabase = create_client(supabase_url, supabase_service_key)
        print("✅ Подключение к Supabase установлено")
        
    except ImportError:
        print("❌ Ошибка: Модуль supabase-py не установлен")
        print("   Установите: pip install supabase")
        return False
    
    # Список миграций в порядке выполнения
    migrations = [
        '001_create_users_table.sql',
        '002_create_goals_table.sql',
        '003_create_progress_log_table.sql',
        '004_create_daily_checkins_table.sql',
        '005_create_settings_table.sql',
        '006_create_sessions_table.sql',  # Опционально
        '007_create_triggers.sql',
    ]
    
    migrations_dir = Path(__file__).parent
    
    print("\n" + "=" * 60)
    print("Выполнение миграций базы данных")
    print("=" * 60 + "\n")
    
    for migration_file in migrations:
        migration_path = migrations_dir / migration_file
        
        if not migration_path.exists():
            if migration_file == '006_create_sessions_table.sql':
                print(f"⏭️  Пропущена опциональная миграция: {migration_file}")
                continue
            else:
                print(f"❌ Файл миграции не найден: {migration_file}")
                return False
        
        print(f"📄 Выполняется: {migration_file}")
        
        try:
            # Читаем SQL файл
            with open(migration_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # Выполняем SQL через Supabase
            # Примечание: Supabase Python клиент не поддерживает прямой SQL,
            # поэтому нужно использовать REST API или psql
            # Для миграций рекомендуется использовать Supabase Dashboard или psql
            
            print(f"⚠️  ВНИМАНИЕ: Supabase Python клиент не поддерживает выполнение произвольного SQL")
            print(f"   Используйте один из вариантов:")
            print(f"   1. Supabase Dashboard → SQL Editor")
            print(f"   2. psql командная строка")
            print(f"   3. Выполните SQL вручную из файла: {migration_path}")
            print()
            
            # Альтернатива: можно использовать psycopg2 для прямого выполнения SQL
            # Но это требует дополнительной настройки подключения
            
        except Exception as e:
            print(f"❌ Ошибка при выполнении миграции {migration_file}: {e}")
            return False
    
    print("=" * 60)
    print("✅ Все миграции подготовлены к выполнению")
    print("=" * 60)
    print("\n📝 Следующие шаги:")
    print("   1. Откройте Supabase Dashboard → SQL Editor")
    print("   2. Скопируйте содержимое каждого файла миграции")
    print("   3. Выполните миграции по порядку")
    print("\n   Или используйте psql для автоматического выполнения")
    
    return True


if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)

