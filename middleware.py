"""
Middleware для авторизации пользователей через Telegram User ID.
Автоматически создает пользователя при первом обращении и сохраняет user_id в context.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from database_supabase import SupabaseDatabase

logger = logging.getLogger(__name__)

# Глобальный экземпляр базы данных
db = SupabaseDatabase()


async def user_auth_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Middleware для авторизации пользователя через Telegram User ID.
    
    Автоматически:
    1. Получает telegram_user_id из update
    2. Создает или получает пользователя в БД
    3. Сохраняет user_id в context.user_data для использования в командах
    4. Инициализирует дефолтные цели для нового пользователя
    """
    try:
        # Получаем данные пользователя из Telegram
        if not update.effective_user:
            logger.warning("Update не содержит информацию о пользователе")
            return
        
        telegram_user_id = update.effective_user.id
        telegram_data = {
            'id': telegram_user_id,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'username': update.effective_user.username,
            'language_code': update.effective_user.language_code
        }
        
        # Получаем или создаем пользователя
        user = db.get_or_create_user(telegram_user_id, telegram_data)
        user_id = user['id']
        
        # Сохраняем user_id в context для использования в командах
        context.user_data['user_id'] = user_id
        context.user_data['telegram_user_id'] = telegram_user_id
        
        # Если пользователь только что создан - инициализируем дефолтные цели
        # Проверяем по created_at (если создан менее минуты назад)
        from datetime import datetime, timedelta
        created_at = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
        if (datetime.now(created_at.tzinfo) - created_at) < timedelta(minutes=1):
            logger.info(f"Новый пользователь создан: {user_id}, инициализируем дефолтные цели")
            db.init_default_goals(user_id)
        
        logger.debug(f"Пользователь авторизован: user_id={user_id}, telegram_id={telegram_user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка в middleware авторизации: {e}")
        # Не блокируем выполнение команды, но логируем ошибку


def get_user_id_from_context(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Получить user_id из context.
    
    Args:
        context: Context бота
    
    Returns:
        str: UUID пользователя
    
    Raises:
        ValueError: Если user_id не найден в context
    """
    user_id = context.user_data.get('user_id')
    if not user_id:
        raise ValueError("user_id не найден в context. Убедитесь, что middleware авторизации выполнен.")
    return user_id

