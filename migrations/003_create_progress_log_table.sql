-- Миграция 003: Создание таблицы progress_log
-- Описание: Таблица для хранения истории изменений прогресса по целям

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

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_progress_log_goal_id ON progress_log(goal_id);
CREATE INDEX IF NOT EXISTS idx_progress_log_user_id ON progress_log(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_log_date ON progress_log(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_progress_log_user_goal ON progress_log(user_id, goal_id, logged_at DESC);

-- Комментарии к таблице и полям
COMMENT ON TABLE progress_log IS 'История изменений прогресса по целям';
COMMENT ON COLUMN progress_log.goal_id IS 'ID цели, к которой относится запись';
COMMENT ON COLUMN progress_log.user_id IS 'ID пользователя (для дополнительной изоляции данных)';
COMMENT ON COLUMN progress_log.note IS 'Примечание к изменению прогресса';

