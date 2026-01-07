#!/usr/bin/env python3
"""
Скрипт для проверки совместимости зависимостей перед установкой.
Проверяет конфликты версий между пакетами.
"""
import subprocess
import sys
import re

def check_pip_resolve():
    """Проверить, может ли pip разрешить все зависимости"""
    print("🔍 Проверка совместимости зависимостей...")
    
    try:
        # Попробуем выполнить dry-run установки
        result = subprocess.run(
            ['pip', 'install', '--dry-run', '-r', 'requirements.txt'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Все зависимости совместимы!")
            return True
        else:
            print("❌ Обнаружены конфликты зависимостей:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Проверка заняла слишком много времени")
        return False
    except FileNotFoundError:
        print("⚠️  pip не найден. Установите pip.")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False

def check_requirements_file():
    """Проверить синтаксис requirements.txt"""
    print("\n🔍 Проверка синтаксиса requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Проверяем формат
            if '==' in line:
                parts = line.split('==')
                if len(parts) != 2:
                    issues.append(f"Строка {i}: неверный формат версии")
            elif '>=' in line:
                parts = line.split('>=')
                if len(parts) != 2:
                    issues.append(f"Строка {i}: неверный формат версии")
            elif '<' in line:
                # Проверяем диапазоны типа ">=0.25.2,<0.29"
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) != 2:
                        issues.append(f"Строка {i}: неверный формат диапазона")
        
        if issues:
            print("❌ Найдены проблемы:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ Синтаксис requirements.txt корректен")
            return True
            
    except FileNotFoundError:
        print("❌ Файл requirements.txt не найден")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False

def main():
    """Главная функция"""
    print("=" * 60)
    print("Проверка совместимости зависимостей")
    print("=" * 60)
    
    # Проверяем синтаксис
    syntax_ok = check_requirements_file()
    
    if not syntax_ok:
        print("\n❌ Исправьте ошибки в requirements.txt перед проверкой совместимости")
        return 1
    
    # Проверяем совместимость
    compatible = check_pip_resolve()
    
    print("\n" + "=" * 60)
    if compatible:
        print("✅ Все проверки пройдены! Можно устанавливать зависимости.")
        return 0
    else:
        print("❌ Обнаружены конфликты. Исправьте requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())

