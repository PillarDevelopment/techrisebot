-- Миграция 005: Создание таблицы settings
-- Описание: Таблица для хранения настроек пользователей

CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_setting UNIQUE (user_id, key)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id);
CREATE INDEX IF NOT EXISTS idx_settings_user_key ON settings(user_id, key);

-- Комментарии к таблице и полям
COMMENT ON TABLE settings IS 'Настройки пользователей';
COMMENT ON COLUMN settings.user_id IS 'ID пользователя';
COMMENT ON COLUMN settings.key IS 'Ключ настройки (например, notifications_enabled)';
COMMENT ON COLUMN settings.value IS 'Значение настройки';

