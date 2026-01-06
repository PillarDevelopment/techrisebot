"""
Главный файл Telegram бота для отслеживания целей.
Здесь обрабатываются команды и сообщения от пользователей.
"""
import logging
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
from database import Database
from goals import GoalsCalculator
from scheduler import NotificationScheduler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных и калькулятора
db = Database()
db.init_default_goals()
calculator = GoalsCalculator(db)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    Приветствует пользователя и показывает список доступных команд
    """
    welcome_message = (
        "🎯 Привет! Я твой трекер целей на 2026 год.\n\n"
        "📋 Доступные команды:\n"
        "/today - сводка на сегодня\n"
        "/goals - список всех целей\n"
        "/update [категория] [значение] - обновить прогресс\n"
        "/report - недельный отчет\n"
        "/log [текст] - добавить запись в дневник\n"
        "/remind [on/off] - включить/выключить уведомления\n\n"
        "Примеры:\n"
        "/update вес 85\n"
        "/update доход 500000\n"
        "/update тренировки 3\n"
        "/update страны +1"
    )
    await update.message.reply_text(welcome_message)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /today
    Показывает сводку на сегодня с прогрессом по целям
    """
    try:
        summary = calculator.get_today_summary()
        await update.message.reply_text(summary)
    except Exception as e:
        logger.error(f"Ошибка в команде /today: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении сводки")


async def goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /goals
    Показывает список всех целей с их статусом
    """
    try:
        goals_list = calculator.get_goals_list()
        await update.message.reply_text(goals_list)
    except Exception as e:
        logger.error(f"Ошибка в команде /goals: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении списка целей")


async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /update
    Обновляет прогресс по цели
    
    Формат: /update [категория/название] [значение]
    Примеры:
    /update вес 85
    /update доход 500000
    /update тренировки 3
    /update страны +1
    """
    try:
        # Проверяем, что пользователь указал аргументы
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Неверный формат команды.\n\n"
                "Использование: /update [категория/название] [значение]\n\n"
                "Примеры:\n"
                "/update вес 85\n"
                "/update доход 500000\n"
                "/update тренировки 3\n"
                "/update страны +1"
            )
            return
        
        # Получаем аргументы
        goal_name = context.args[0].lower()
        value_str = context.args[1]
        
        # Парсим значение (может быть число или +1, -1 и т.д.)
        if value_str.startswith('+') or value_str.startswith('-'):
            # Относительное изменение
            change = float(value_str)
            # Находим цель и обновляем относительно текущего значения
            goals_list = db.get_goals_by_category()
            goal_found = None
            
            for goal in goals_list:
                if goal_name in goal['name'].lower() or goal_name in goal['category'].lower():
                    goal_found = goal
                    break
            
            if goal_found:
                new_value = goal_found['current_value'] + change
                db.update_goal_value(goal_found['id'], new_value)
                await update.message.reply_text(
                    f"✅ Обновлено: {goal_found['name']}\n"
                    f"Было: {goal_found['current_value']:.0f}\n"
                    f"Стало: {new_value:.0f}"
                )
            else:
                await update.message.reply_text(f"❌ Цель '{goal_name}' не найдена")
        else:
            # Абсолютное значение
            try:
                value = float(value_str)
                
                # Маппинг названий целей
                goal_mapping = {
                    'вес': ('спорт', 'Вес'),
                    'доход': ('финансы', None),  # Специальная обработка для дохода
                    'тренировки': ('спорт', 'Тренировки в неделю'),
                    'тренировка': ('спорт', 'Тренировки в неделю'),
                    'страны': ('путешествия', 'Новые страны'),
                    'страна': ('путешествия', 'Новые страны'),
                    'марафоны': ('спорт', 'Марафоны'),
                    'марафон': ('спорт', 'Марафоны'),
                    'машина': ('покупки', 'Voyah Free (авто)'),
                    'авто': ('покупки', 'Voyah Free (авто)'),
                    'квартира': ('покупки', 'Квартира в Москве'),
                }
                
                # Специальная обработка для дохода - обновляем актуальную цель
                if goal_name == 'доход':
                    from datetime import date
                    goals_list = db.get_goals_by_category('финансы')
                    # Находим актуальную цель по доходу в зависимости от месяца
                    current_month = date.today().month
                    goal_found = None
                    
                    if current_month <= 2:  # Январь-Февраль
                        goal_name_to_find = 'Доход 1М/мес'
                    elif current_month <= 5:  # Март-Май
                        goal_name_to_find = 'Доход 2М/мес'
                    else:  # Июнь и далее
                        goal_name_to_find = 'Доход 5М/мес'
                    
                    for goal in goals_list:
                        if goal_name_to_find in goal['name']:
                            goal_found = goal
                            break
                    
                    if goal_found:
                        db.update_goal_value(goal_found['id'], value)
                        await update.message.reply_text(
                            f"✅ Обновлено: {goal_found['name']} = {value:,.0f} ₽"
                        )
                    else:
                        await update.message.reply_text("❌ Не найдена цель по доходу")
                    return
                
                # Специальная обработка для тренировок (да/нет)
                if goal_name in ['тренировка', 'тренировки'] and value_str.lower() in ['да', 'yes', '1', 'true']:
                    # Увеличиваем счетчик тренировок на 1
                    goals_list = db.get_goals_by_category('спорт')
                    workout_goal = None
                    for goal in goals_list:
                        if 'Тренировки' in goal['name']:
                            workout_goal = goal
                            break
                    
                    if workout_goal:
                        new_value = workout_goal['current_value'] + 1
                        db.update_goal_value(workout_goal['id'], new_value)
                        await update.message.reply_text(
                            f"✅ Тренировка засчитана! Всего тренировок на этой неделе: {new_value:.0f}"
                        )
                    else:
                        await update.message.reply_text("❌ Цель по тренировкам не найдена")
                    return
                
                # Ищем цель
                if goal_name in goal_mapping:
                    category, name = goal_mapping[goal_name]
                    if name:  # Если name не None (не специальный случай)
                        db.update_goal_by_name(category, name, value)
                        await update.message.reply_text(f"✅ Обновлено: {name} = {value:.0f}")
                else:
                    # Пытаемся найти по названию или категории
                    goals_list = db.get_goals_by_category()
                    goal_found = None
                    
                    for goal in goals_list:
                        if goal_name in goal['name'].lower() or goal_name in goal['category'].lower():
                            goal_found = goal
                            break
                    
                    if goal_found:
                        db.update_goal_value(goal_found['id'], value)
                        await update.message.reply_text(
                            f"✅ Обновлено: {goal_found['name']} = {value:.0f}"
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ Цель '{goal_name}' не найдена.\n"
                            f"Используйте: вес, доход, тренировки, страны, марафоны, машина, квартира"
                        )
            except ValueError:
                await update.message.reply_text("❌ Неверный формат значения. Используйте число.")
    
    except Exception as e:
        logger.error(f"Ошибка в команде /update: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обновлении цели")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /report
    Показывает недельный отчет с прогрессом
    """
    try:
        report_text = calculator.get_weekly_report()
        await update.message.reply_text(report_text)
    except Exception as e:
        logger.error(f"Ошибка в команде /report: {e}")
        await update.message.reply_text("❌ Произошла ошибка при генерации отчета")


async def log_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /log
    Добавляет запись в дневник прогресса
    """
    try:
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите текст записи.\n"
                "Пример: /log Сегодня отлично потренировался!"
            )
            return
        
        note = ' '.join(context.args)
        db.add_daily_checkin(notes=note)
        await update.message.reply_text(f"✅ Запись добавлена: {note}")
    
    except Exception as e:
        logger.error(f"Ошибка в команде /log: {e}")
        await update.message.reply_text("❌ Произошла ошибка при добавлении записи")


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /remind
    Включает или выключает уведомления
    """
    try:
        if not context.args:
            current = db.get_setting('notifications_enabled', 'on')
            status = "включены" if current == 'on' else "выключены"
            await update.message.reply_text(
                f"📢 Уведомления сейчас {status}.\n"
                f"Используйте: /remind on или /remind off"
            )
            return
        
        action = context.args[0].lower()
        if action == 'on':
            db.set_setting('notifications_enabled', 'on')
            await update.message.reply_text("✅ Уведомления включены")
        elif action == 'off':
            db.set_setting('notifications_enabled', 'off')
            await update.message.reply_text("🔕 Уведомления выключены")
        else:
            await update.message.reply_text("❌ Используйте: /remind on или /remind off")
    
    except Exception as e:
        logger.error(f"Ошибка в команде /remind: {e}")
        await update.message.reply_text("❌ Произошла ошибка")


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /skip
    Пропускает вечерний опрос
    """
    await update.message.reply_text("✅ Пропущено. Хорошего вечера! 🌙")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """
    Главная функция для запуска бота
    """
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен! Создайте файл .env")
        return
    
    if not TELEGRAM_USER_ID:
        logger.error("TELEGRAM_USER_ID не установлен! Создайте файл .env")
        return
    
    # Создаем приложение бота
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("goals", goals))
    application.add_handler(CommandHandler("update", update))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("log", log_entry))
    application.add_handler(CommandHandler("remind", remind))
    application.add_handler(CommandHandler("skip", skip))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Настраиваем планировщик уведомлений
    scheduler = NotificationScheduler(application.bot, TELEGRAM_USER_ID)
    scheduler.start()
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    logger.info(f"Уведомления будут отправляться пользователю с ID: {TELEGRAM_USER_ID}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

