# ⚡ Быстрое развертывание на сервере

## Быстрая установка (systemd)

```bash
# 1. Подключитесь к серверу
ssh user@your-server.com

# 2. Установите зависимости системы
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

# 3. Создайте директорию и загрузите проект
mkdir -p ~/techrisebot && cd ~/techrisebot
# Загрузите файлы проекта (scp, git, или другой способ)

# 4. Настройте окружение
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Создайте .env файл
nano .env
# Добавьте:
# TELEGRAM_BOT_TOKEN=ваш_токен
# TELEGRAM_USER_ID=ваш_id

# 6. Настройте systemd сервис
# Отредактируйте techrisebot.service, заменив YOUR_USERNAME на ваше имя пользователя
sudo cp techrisebot.service /etc/systemd/system/techrisebot.service
sudo nano /etc/systemd/system/techrisebot.service  # Замените YOUR_USERNAME

# 7. Запустите
sudo systemctl daemon-reload
sudo systemctl enable techrisebot
sudo systemctl start techrisebot
sudo systemctl status techrisebot
```

## Полезные команды

```bash
# Просмотр логов
sudo journalctl -u techrisebot -f

# Перезапуск
sudo systemctl restart techrisebot

# Остановка
sudo systemctl stop techrisebot

# Статус
sudo systemctl status techrisebot
```

## Быстрый вариант (screen)

```bash
screen -S techrisebot
source venv/bin/activate
python3 bot.py
# Ctrl+A, затем D для отключения
```

## Проверка работы

```bash
# В Telegram напишите боту: /start
# Проверьте логи: tail -f bot.log
```

