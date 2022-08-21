import os
import time

import requests

from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
print(HEADERS)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
MONTH_IN_SEC = 2629743


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    response = response.json()
    return response

    ...


def check_response(response):
    """
    Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API, приведенный к
    типам данных Python.
    Если ответ API соответствует ожиданиям, то функция должна вернуть список
    домашних работ (он может быть и пустым),
    доступный в ответе API по ключу 'homeworks'.
    """
    homeworks = response['homeworks']
    if not (isinstance(response, dict)):
        # logger.error('Ответ сервера не является словарем!')
        raise TypeError('Ответ сервера не является словарем!')
    return homeworks

    ...


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    """
    homework_name = ...
    homework_status = ...

    ...

    verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ...


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = (int(time.time())) - MONTH_IN_SEC

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
