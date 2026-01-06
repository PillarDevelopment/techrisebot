"""
Конфигурационный файл для бота.
Здесь хранятся настройки и константы.
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота от BotFather
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ID пользователя Telegram (чтобы бот отправлял уведомления только вам)
TELEGRAM_USER_ID = int(os.getenv('TELEGRAM_USER_ID', '0'))

# Название файла базы данных
DATABASE_NAME = 'goals.db'

# Часовой пояс для уведомлений (МСК = UTC+3)
TIMEZONE = 'Europe/Moscow'

# Время утренних уведомлений (9:00 МСК)
MORNING_HOUR = 9
MORNING_MINUTE = 0

# Время вечерних уведомлений (21:00 МСК)
EVENING_HOUR = 21
EVENING_MINUTE = 0

