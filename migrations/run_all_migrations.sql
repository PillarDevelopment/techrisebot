-- ⚠️ ВНИМАНИЕ: Этот файл использует команды psql (\i)
-- Для Supabase Dashboard SQL Editor используйте файл: 00_all_migrations.sql
--
-- Этот файл предназначен только для выполнения через psql командную строку:
-- psql "postgresql://postgres:[PASSWORD]@[PROJECT].supabase.co:5432/postgres" -f run_all_migrations.sql

-- Миграция 001: Создание таблицы users
\i 001_create_users_table.sql

-- Миграция 002: Создание таблицы goals
\i 002_create_goals_table.sql

-- Миграция 003: Создание таблицы progress_log
\i 003_create_progress_log_table.sql

-- Миграция 004: Создание таблицы daily_checkins
\i 004_create_daily_checkins_table.sql

-- Миграция 005: Создание таблицы settings
\i 005_create_settings_table.sql

-- Миграция 006: Создание таблицы sessions (опционально)
-- Раскомментируйте следующую строку, если нужна таблица sessions:
-- \i 006_create_sessions_table.sql

-- Миграция 007: Создание триггеров
\i 007_create_triggers.sql

-- Проверка выполнения
SELECT 'Миграции выполнены успешно!' AS status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

