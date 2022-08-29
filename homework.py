"""Бот для проверки домашки."""
import os
import sys
import time
import logging
from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv

from exceptions import (BotException, ExceptionNot200Error, ExceptionTelegram,
                        ExceptionResponseError, ExceptionListEmpty,
                        ExceptionNonInspectedError, ExceptionStatusUnknown)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
MONTH_IN_SEC = 2629743

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler(sys.stdout)
logger.addHandler(streamHandler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.info('The bot started sending a message')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError:
        logger.info('The bot failed to send the message!')
        raise ExceptionTelegram
    else:
        logger.info('The bot did a great job in sending the message!')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info('Work has begun on the API request.')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as request_error:
        message = f'Код ответа API (RequestException): {request_error}'
        raise ExceptionNonInspectedError(message)
    else:
        if response.status_code != HTTPStatus.OK:
            message = 'The request page is unavailable! Repeat later!'
            raise ExceptionNot200Error(message)
        logger.info('Request completed successfully.')
        return response.json()


def check_response(response):
    """
    Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API, приведенный к
    типам данных Python.
    Если ответ API соответствует ожиданиям, то функция должна вернуть список
    домашних работ (он может быть и пустым),
    доступный в ответе API по ключу 'homeworks'.
    """
    if not (isinstance(response, dict)):
        message = 'Ответ сервера не является словарем!'
        raise TypeError(message)

    homeworks = response.get('homeworks')

    if 'homeworks' not in response:
        message = 'There is no "homework" key in the response'
        raise ExceptionResponseError(message)

    if homeworks is None:
        message = 'Response Error!'
        raise ExceptionResponseError(message)

    if not isinstance(homeworks, list):
        message = 'Домашка с сервера не является списком!'
        raise TypeError(message)
    if not homeworks:
        message = 'Список домашних работ пуст!'
        raise ExceptionListEmpty(message)
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной.
    домашней работе статус этой работы.
    """
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Status hw unknown!'
        logger.error(message)
        raise ExceptionStatusUnknown(message)
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения.
    которые необходимы для работы программы.
    """
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    logger.debug('start check tokens:')
    check_tokens()
    if not check_tokens():
        logger.critical('Tokens is not found!')
        message = 'The program has failed, there are no tokens!'
        sys.exit(message)
    logger.debug('tokens correct!')

    last_message = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            current_timestamp = int(time.time()) - MONTH_IN_SEC

            response = get_api_answer(current_timestamp)
            logger.debug('get_api_answer is good.')

            homeworks = check_response(response)
            homework = homeworks[0]
            message = parse_status(homework)

            if message != last_message:
                send_message(bot, message)
                last_message = message

        except ExceptionListEmpty as e:
            logger.info(str(e))

        except BotException as error:
            message = f'Ошибка в программе: {str(error)}'
            logger.exception(f'Error: {message}!!!')
            if message != last_message:
                send_message(bot, message)
                last_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
