# Финальное исправление ошибки "proxy argument"

## Проблема

Ошибка `Client.__init__() got an unexpected keyword argument 'proxy'` все еще возникает даже после обновления кода.

## Решение: Обновить до последних версий

### Шаг 1: Обновите код (если используете git)

```bash
cd /root/techrisebot
git pull
```

Или скопируйте обновленные файлы `database_supabase.py` и `requirements.txt`.

### Шаг 2: Полностью переустановите supabase и зависимости

```bash
cd /root/techrisebot
source venv/bin/activate

# Удалите все проблемные библиотеки
pip uninstall supabase postgrest storage3 realtime httpx -y

# Обновите pip
pip install --upgrade pip setuptools wheel

# Установите последнюю версию supabase (она автоматически установит совместимые зависимости)
pip install --upgrade supabase

# Установите остальные зависимости
pip install -r requirements.txt
```

### Шаг 3: Если не помогло - пересоздайте venv

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

# Установите зависимости (теперь с обновленными версиями)
pip install -r requirements.txt

# Проверьте версии
pip list | grep -E "(supabase|httpx|postgrest)"
```

### Шаг 4: Проверьте подключение

```bash
python3 check_deployment.py
```

## Альтернативное решение: Использовать конкретную рабочую версию

Если обновление не помогло, попробуйте установить конкретные версии, которые точно работают:

```bash
cd /root/techrisebot
source venv/bin/activate

# Удалите все
pip uninstall supabase postgrest storage3 realtime httpx -y

# Установите конкретные версии
pip install supabase==2.8.0
pip install httpx==0.27.0

# Установите остальные зависимости
pip install python-telegram-bot==20.7 APScheduler==3.10.4 python-dotenv==1.0.0 pytz==2024.1 psycopg2-binary
```

## Проверка версий после установки

```bash
pip show supabase httpx postgrest
```

Должны быть установлены:
- supabase: 2.8.0 или выше
- httpx: 0.27.0 или выше
- postgrest: установится автоматически

## Если все еще не работает

Попробуйте использовать самую последнюю версию supabase:

```bash
pip install --upgrade supabase httpx
```

Или попробуйте более старую стабильную версию:

```bash
pip install supabase==2.0.3 httpx==0.25.2
```

После каждого изменения проверяйте:

```bash
python3 check_deployment.py
```

