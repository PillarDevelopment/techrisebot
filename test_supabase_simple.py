#!/usr/bin/env python3
"""
Простой тест создания клиента Supabase без реального подключения.
Проверяет только импорты и создание объекта клиента.
"""
import os
import sys

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Проверка импортов"""
    print("🔍 Проверка импортов...")
    try:
        from supabase import create_client, Client
        print("✅ Импорт supabase успешен")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_client_creation():
    """Проверка создания клиента"""
    print("\n🔍 Проверка создания клиента...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL или SUPABASE_KEY не установлены")
        return False
    
    try:
        from supabase import create_client
        
        # Пробуем создать клиент
        client = create_client(supabase_url, supabase_key)
        print("✅ Клиент Supabase создан успешно!")
        print(f"✅ URL: {supabase_url[:30]}...")
        print(f"✅ Key: {supabase_key[:20]}...")
        return True
    except TypeError as e:
        error_msg = str(e)
        if "proxy" in error_msg.lower() or "unexpected keyword argument" in error_msg.lower():
            print(f"❌ Ошибка версии библиотеки: {e}")
            print("\n💡 Решение:")
            print("   pip uninstall supabase -y")
            print("   pip install supabase==2.3.4")
            return False
        else:
            print(f"❌ Ошибка создания клиента: {e}")
            return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def main():
    """Главная функция"""
    print("=" * 60)
    print("Тест создания клиента Supabase")
    print("=" * 60)
    
    # Проверяем импорты
    if not test_imports():
        return 1
    
    # Проверяем создание клиента
    if not test_client_creation():
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Все проверки пройдены!")
    print("=" * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())

