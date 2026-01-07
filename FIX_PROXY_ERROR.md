# Исправление ошибки "unexpected keyword argument 'proxy'"

## Проблема

Ошибка `Client.__init__() got an unexpected keyword argument 'proxy'` возникает из-за конфликта версий библиотеки `supabase-py` и её зависимостей.

## Решение

### Шаг 1: Обновите код (уже сделано)

Код в `database_supabase.py` обновлен для использования именованных параметров и обработки ошибок версий.

### Шаг 2: Переустановите зависимости на сервере

```bash
cd /root/techrisebot
source venv/bin/activate

# Удалите старые версии
pip uninstall supabase postgrest storage3 realtime -y

# Обновите pip
pip install --upgrade pip setuptools wheel

# Установите все зависимости заново
pip install -r requirements.txt
```

### Шаг 3: Если проблема сохраняется - пересоздайте venv

```bash
cd /root/techrisebot

# Удалите старое окружение
rm -rf venv

# Создайте новое
python3 -m venv venv

# Активируйте
source venv/bin/activate

# Обновите pip
pip install --upgrade pip setuptools wheel

# Установите зависимости
pip install -r requirements.txt

# Проверьте версии
pip list | grep -E "(supabase|postgrest|storage|realtime|httpx)"
```

### Шаг 4: Проверьте подключение

```bash
python3 check_deployment.py
```

Должно быть:
```
✅ PASS: Подключение к Supabase
```

## Альтернативное решение: Использовать конкретные версии

Если проблема все еще возникает, попробуйте зафиксировать конкретные версии всех зависимостей:

```bash
pip install supabase==2.3.4 postgrest==0.13.0 storage3==0.7.0 realtime==2.0.0 httpx==0.28.1
```

## Проверка установленных версий

```bash
pip show supabase postgrest storage3 realtime httpx
```

Должны быть установлены:
- supabase: 2.3.4
- postgrest: 0.13.0 или выше
- storage3: 0.7.0 или выше
- realtime: 2.0.0 или выше
- httpx: 0.25.2 - 0.28.x

## Если ничего не помогает

Попробуйте использовать более старую стабильную версию:

```bash
pip install supabase==2.0.0
```

Или самую новую версию:

```bash
pip install --upgrade supabase
```

После этого проверьте подключение снова.

