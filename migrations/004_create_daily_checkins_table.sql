-- Миграция 004: Создание таблицы daily_checkins
-- Описание: Таблица для хранения ежедневных отметок пользователей

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

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_daily_checkins_user_id ON daily_checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_checkins_date ON daily_checkins(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_checkins_user_date_range ON daily_checkins(user_id, date DESC);

-- Комментарии к таблице и полям
COMMENT ON TABLE daily_checkins IS 'Ежедневные отметки пользователей';
COMMENT ON COLUMN daily_checkins.user_id IS 'ID пользователя';
COMMENT ON COLUMN daily_checkins.date IS 'Дата отметки (YYYY-MM-DD)';
COMMENT ON COLUMN daily_checkins.workout IS 'Была ли тренировка в этот день';
COMMENT ON COLUMN daily_checkins.income IS 'Доход за день в рублях';

