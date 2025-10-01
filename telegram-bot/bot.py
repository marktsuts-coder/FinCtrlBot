import requests
from bs4 import BeautifulSoup
import time
import schedule
from urllib.parse import urljoin
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime
import re
import os
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print(f"=== ЗАПУСК ТЕЛЕГРАМ БОТА ===")
print(f"🤖 Бот инициализирован с токеном: {BOT_TOKEN[:10]}...")
print(f"📢 Канал: {CHANNEL_ID}")

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
DATA_FILE = 'posted_links.json'

# Добавьте проверку
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Добавьте его в переменные окружения")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не установлен! Добавьте его в переменные окружения")

# Минимальная дата для публикации
MIN_DATE = datetime(2025, 9, 20)

# Два раздела для отслеживания
SITES_TO_CHECK = [
    {
        'url': 'https://rufincontrol.ru/articles/',
        'name': 'Публикации',
        'type': 'article',
        'domain': 'rufincontrol.ru'
    },
    {
        'url': 'https://rufincontrol.ru/online/',
        'name': 'Электронный журнал',
        'type': 'journal',
        'domain': 'rufincontrol.ru'
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Функции для работы с данными
def load_posted_links():
    """Загружает ссылки из JSON файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return set()

def save_posted_links(links):
    """Сохраняет ссылки в JSON файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(links), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

# Инициализация данных
posted_links_cache = load_posted_links()

def get_posted_links():
    return posted_links_cache

def save_link(link):
    posted_links_cache.add(link)
    save_posted_links(posted_links_cache)
    logger.info(f"Ссылка сохранена (всего: {len(posted_links_cache)})")

# Остальные функции остаются без изменений...
# [Вставьте сюда все остальные функции из вашего кода]

def main():
    logger.info("🤖 Бот инициализирован")
    print("📊 Отслеживаемые разделы:")
    for site in SITES_TO_CHECK:
        print(f"   • {site['name']} ({site['url']})")
    print(f"📅 Фильтр по дате: от {MIN_DATE.strftime('%d.%m.%Y')}")
    print(f"💾 Сохранение ссылок: JSON файл ({len(posted_links_cache)} ссылок загружено)")
    
    # Первая проверка сразу
    parse_news()
    
    # Настройка расписания
    schedule.every(20).minutes.do(parse_news)
    
    # Основной цикл
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")
        print(f"📊 Всего обработано ссылок: {len(posted_links_cache)}")

if __name__ == "__main__":
    main()
