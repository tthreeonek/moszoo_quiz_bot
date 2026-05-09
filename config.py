import os

# Настройки бота
BOT_TOKEN = "ваш_токен_от_BotFather"
ADMIN_CHAT_ID = 123456789          # ваш Telegram ID (число)
BOT_USERNAME = "@MyZooBot"        # юзернейм бота (без пробелов)

# Контакты зоопарка
ZOO_EMAIL = "zoo@moscowzoo.ru"
ZOO_PHONE = "+7 (499) 255-00-93"
OPECKA_URL = "https://moscowzoo.ru/about/guardianship"

# Настройки прокси (если нужен). Если нет - оставь пустые строки (МОЖНО ПРОСТО ВРУБИТЬ VPN и запустить так)
PROXY_URL = ""          # например "socks5://127.0.0.1:10808"
GET_UPDATES_PROXY = ""  # обычно такой же

# Путь к папке с изображениями
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.jpg")