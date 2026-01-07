-- Миграция 006: Создание таблицы sessions (опционально)
-- Описание: Таблица для отслеживания активных сессий и статистики использования

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    command_count INTEGER DEFAULT 0,
    
    CONSTRAINT positive_command_count CHECK (command_count >= 0)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_activity ON sessions(user_id, last_activity DESC);

-- Комментарии к таблице и полям
COMMENT ON TABLE sessions IS 'Активные сессии пользователей (для статистики)';
COMMENT ON COLUMN sessions.user_id IS 'ID пользователя';
COMMENT ON COLUMN sessions.started_at IS 'Время начала сессии';
COMMENT ON COLUMN sessions.last_activity IS 'Время последней активности';
COMMENT ON COLUMN sessions.command_count IS 'Количество выполненных команд в сессии';

