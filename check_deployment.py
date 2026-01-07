#!/usr/bin/env python3
"""
Скрипт для проверки готовности к деплою на удаленном сервере.
Проверяет наличие всех зависимостей и переменных окружения.
"""
import sys
import os

def check_env_file():
    """Проверить наличие .env файла и переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        return False
    
    # Загружаем переменные из .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv не установлен, проверяю системные переменные...")
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} не установлен")
        else:
            # Показываем только первые и последние символы для безопасности
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"✅ {var} = {masked}")
    
    if missing_vars:
        print(f"\n❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    return True

def check_dependencies():
    """Проверить наличие всех зависимостей"""
    print("\n🔍 Проверка зависимостей...")
    
    required_packages = [
        'telegram',
        'supabase',
        'psycopg2',
        'apscheduler',
        'pytz',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'telegram':
                import telegram
            elif package == 'supabase':
                import supabase
            elif package == 'psycopg2':
                import psycopg2
            elif package == 'apscheduler':
                import apscheduler
            elif package == 'pytz':
                import pytz
            elif package == 'python-dotenv':
                import dotenv
            
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите: pip install -r requirements.txt")
        return False
    
    return True

def check_imports():
    """Проверить импорты основных модулей"""
    print("\n🔍 Проверка импортов...")
    
    modules = [
        'config',
        'database_supabase',
        'goals',
        'scheduler',
        'middleware',
        'bot'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} импортирован успешно")
        except Exception as e:
            print(f"❌ Ошибка импорта {module}: {e}")
            failed_imports.append((module, str(e)))
    
    if failed_imports:
        print("\n❌ Ошибки импорта:")
        for module, error in failed_imports:
            print(f"  {module}: {error}")
        return False
    
    return True

def check_supabase_connection():
    """Проверить подключение к Supabase"""
    print("\n🔍 Проверка подключения к Supabase...")
    
    try:
        from database_supabase import SupabaseDatabase
        db = SupabaseDatabase()
        print("✅ Подключение к Supabase установлено")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return False

def main():
    """Главная функция"""
    print("=" * 60)
    print("Проверка готовности к деплою")
    print("=" * 60)
    
    checks = [
        ("Переменные окружения", check_env_file),
        ("Зависимости", check_dependencies),
        ("Импорты", check_imports),
        ("Подключение к Supabase", check_supabase_connection)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Результаты проверки:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ Все проверки пройдены! Бот готов к запуску.")
        return 0
    else:
        print("❌ Некоторые проверки не пройдены. Исправьте ошибки перед запуском.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

