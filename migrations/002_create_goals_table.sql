-- Миграция 002: Создание таблицы goals
-- Описание: Таблица для хранения целей пользователей

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

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_category ON goals(user_id, category);
CREATE INDEX IF NOT EXISTS idx_goals_deadline ON goals(user_id, deadline) WHERE deadline IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_goals_user_category ON goals(user_id, category, deadline);

-- Комментарии к таблице и полям
COMMENT ON TABLE goals IS 'Цели пользователей';
COMMENT ON COLUMN goals.user_id IS 'ID пользователя-владельца цели';
COMMENT ON COLUMN goals.category IS 'Категория цели (финансы, спорт, покупки, путешествия)';
COMMENT ON COLUMN goals.initial_value IS 'Начальное значение (для целей с уменьшением, например вес)';

