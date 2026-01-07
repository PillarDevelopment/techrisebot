-- Миграция 001: Создание таблицы users
-- Описание: Таблица для хранения информации о пользователях Telegram

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

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = true;

-- Комментарии к таблице и полям
COMMENT ON TABLE users IS 'Пользователи Telegram бота';
COMMENT ON COLUMN users.telegram_user_id IS 'Уникальный ID пользователя из Telegram (используется для авторизации)';
COMMENT ON COLUMN users.telegram_username IS 'Username пользователя в Telegram (@username)';
COMMENT ON COLUMN users.is_active IS 'Флаг активности пользователя (для блокировки)';

