-- ============================================================================
-- ВСЕ МИГРАЦИИ В ОДНОМ ФАЙЛЕ
-- Для выполнения в Supabase Dashboard SQL Editor
-- ============================================================================
-- 
-- ИНСТРУКЦИЯ:
-- 1. Откройте Supabase Dashboard → SQL Editor
-- 2. Скопируйте весь этот файл
-- 3. Вставьте в SQL Editor
-- 4. Нажмите Run или Ctrl+Enter
--
-- ============================================================================

-- ============================================================================
-- МИГРАЦИЯ 001: Создание таблицы users
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'ru',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_telegram_user UNIQUE (telegram_user_id)
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = true;

COMMENT ON TABLE users IS 'Пользователи Telegram бота';
COMMENT ON COLUMN users.telegram_user_id IS 'Уникальный ID пользователя из Telegram (используется для авторизации)';
COMMENT ON COLUMN users.telegram_username IS 'Username пользователя в Telegram (@username)';
COMMENT ON COLUMN users.is_active IS 'Флаг активности пользователя (для блокировки)';

-- ============================================================================
-- МИГРАЦИЯ 002: Создание таблицы goals
-- ============================================================================

CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    target_value DECIMAL(15,2) NOT NULL,
    current_value DECIMAL(15,2) DEFAULT 0,
    initial_value DECIMAL(15,2),
    unit VARCHAR(50),
    deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_goal UNIQUE (user_id, category, name),
    CONSTRAINT positive_target_value CHECK (target_value >= 0),
    CONSTRAINT positive_current_value CHECK (current_value >= 0)
);

CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_category ON goals(user_id, category);
CREATE INDEX IF NOT EXISTS idx_goals_deadline ON goals(user_id, deadline) WHERE deadline IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_goals_user_category ON goals(user_id, category, deadline);

COMMENT ON TABLE goals IS 'Цели пользователей';
COMMENT ON COLUMN goals.user_id IS 'ID пользователя-владельца цели';
COMMENT ON COLUMN goals.category IS 'Категория цели (финансы, спорт, покупки, путешествия)';
COMMENT ON COLUMN goals.initial_value IS 'Начальное значение (для целей с уменьшением, например вес)';

-- ============================================================================
-- МИГРАЦИЯ 003: Создание таблицы progress_log
-- ============================================================================

CREATE TABLE IF NOT EXISTS progress_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    value DECIMAL(15,2) NOT NULL,
    note TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_progress_log_goal FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
    CONSTRAINT fk_progress_log_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_progress_log_goal_id ON progress_log(goal_id);
CREATE INDEX IF NOT EXISTS idx_progress_log_user_id ON progress_log(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_log_date ON progress_log(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_progress_log_user_goal ON progress_log(user_id, goal_id, logged_at DESC);

COMMENT ON TABLE progress_log IS 'История изменений прогресса по целям';
COMMENT ON COLUMN progress_log.goal_id IS 'ID цели, к которой относится запись';
COMMENT ON COLUMN progress_log.user_id IS 'ID пользователя (для дополнительной изоляции данных)';
COMMENT ON COLUMN progress_log.note IS 'Примечание к изменению прогресса';

-- ============================================================================
-- МИГРАЦИЯ 004: Создание таблицы daily_checkins
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    workout BOOLEAN DEFAULT false,
    income DECIMAL(15,2) DEFAULT 0,
    new_connections INTEGER DEFAULT 0,
    weight DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_date UNIQUE (user_id, date),
    CONSTRAINT positive_income CHECK (income >= 0),
    CONSTRAINT positive_connections CHECK (new_connections >= 0),
    CONSTRAINT positive_weight CHECK (weight > 0 OR weight IS NULL)
);

CREATE INDEX IF NOT EXISTS idx_daily_checkins_user_id ON daily_checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_checkins_date ON daily_checkins(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_checkins_user_date_range ON daily_checkins(user_id, date DESC);

COMMENT ON TABLE daily_checkins IS 'Ежедневные отметки пользователей';
COMMENT ON COLUMN daily_checkins.user_id IS 'ID пользователя';
COMMENT ON COLUMN daily_checkins.date IS 'Дата отметки (YYYY-MM-DD)';
COMMENT ON COLUMN daily_checkins.workout IS 'Была ли тренировка в этот день';
COMMENT ON COLUMN daily_checkins.income IS 'Доход за день в рублях';

-- ============================================================================
-- МИГРАЦИЯ 005: Создание таблицы settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_setting UNIQUE (user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id);
CREATE INDEX IF NOT EXISTS idx_settings_user_key ON settings(user_id, key);

COMMENT ON TABLE settings IS 'Настройки пользователей';
COMMENT ON COLUMN settings.user_id IS 'ID пользователя';
COMMENT ON COLUMN settings.key IS 'Ключ настройки (например, notifications_enabled)';
COMMENT ON COLUMN settings.value IS 'Значение настройки';

-- ============================================================================
-- МИГРАЦИЯ 006: Создание таблицы sessions (ОПЦИОНАЛЬНО)
-- ============================================================================
-- Раскомментируйте следующий блок, если нужна таблица sessions:

/*
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    command_count INTEGER DEFAULT 0,
    
    CONSTRAINT positive_command_count CHECK (command_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_activity ON sessions(user_id, last_activity DESC);

COMMENT ON TABLE sessions IS 'Активные сессии пользователей (для статистики)';
COMMENT ON COLUMN sessions.user_id IS 'ID пользователя';
COMMENT ON COLUMN sessions.started_at IS 'Время начала сессии';
COMMENT ON COLUMN sessions.last_activity IS 'Время последней активности';
COMMENT ON COLUMN sessions.command_count IS 'Количество выполненных команд в сессии';
*/

-- ============================================================================
-- МИГРАЦИЯ 007: Создание триггеров для автоматического обновления updated_at
-- ============================================================================

-- Создаем или заменяем функцию (идемпотентно)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Удаляем триггеры, если они существуют, затем создаем заново (идемпотентно)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_goals_updated_at ON goals;
CREATE TRIGGER update_goals_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_settings_updated_at ON settings;
CREATE TRIGGER update_settings_updated_at
    BEFORE UPDATE ON settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column() IS 'Функция для автоматического обновления поля updated_at';

-- ============================================================================
-- ПРОВЕРКА ВЫПОЛНЕНИЯ МИГРАЦИЙ
-- ============================================================================

-- Проверка созданных таблиц
SELECT 
    '✅ Миграции выполнены успешно!' AS status,
    COUNT(*) AS tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('users', 'goals', 'progress_log', 'daily_checkins', 'settings');

-- Список всех созданных таблиц
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- ============================================================================
-- КОНЕЦ МИГРАЦИЙ
-- ============================================================================

