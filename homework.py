"""Бот для проверки домашки."""
import os
import sys
import time
import logging

import requests
import telegram

from dotenv import load_dotenv

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
    level=logging.INFO,
    stream=sys.stdout,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler('program_hw.log')
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)


class ExceptionNot200Error(Exception):
    """Запрос не вернул ответ с кодом 200."""


class ExceptionTelegram(Exception):
    """Сообщение не отправилось в чат."""


class ExceptionResponseError(Exception):
    """Ошибка отклика."""


class ExceptionTokenError(Exception):
    """Ошибка передачи токена."""


class ExceptionNonInspectedError(Exception):
    """Прочие ошибки."""


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            logger.error('Answer not 200')
            raise ExceptionNot200Error('Answer not 200')
        return response.json()
    except requests.exceptions.RequestException as request_error:
        code_api_msg = f'Код ответа API (RequestException): {request_error}'
        raise Exception(code_api_msg)


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
    if response.get('homeworks') is None:
        raise ExceptionResponseError('Response Error!')
    if not (isinstance(response, dict)):
        logger.error('Ответ сервера не является словарем!')
        raise TypeError('Ответ сервера не является словарем!')
    if not (isinstance(homeworks, list)):
        logger.error('Домашка с сервера не является списком!')
        raise TypeError('Домашка с сервера не является списком!')
    return homeworks


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']

    verdict = HOMEWORK_STATUSES[homework_status]
    print(f'Изменился статус проверки работы "{homework_name}". {verdict}')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения
    которые необходимы для работы программы.
    """
    check = True
    if PRACTICUM_TOKEN is None:
        check = False
    if TELEGRAM_TOKEN is None:
        check = False
    if TELEGRAM_CHAT_ID is None:
        check = False

    return check


def main():
    """Основная логика работы бота."""
    try:
        logger.debug('start check tokens:')
        check_tokens()
        if not check_tokens():
            logger.critical('Tokens is not found!')
            sys.exit(1)
        logger.debug('tokens correct!')

    except ExceptionTokenError:
        logger.critical('Other error with token!')

    message_repeat = ''

    while True:
        try:
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            current_timestamp = (int(time.time())) - MONTH_IN_SEC
            try:
                message = 'Бот начал работу.'
                send_message(bot, message)
                logger.info(f'Message {message} send to Telegram.')
            except telegram.TelegramError:
                logger.error('Error send message to Telegram!')
            try:
                logger.debug('start get_api_answer')
                response = get_api_answer(current_timestamp)
                logger.debug('get_api_answer is good.')
            except Exception:
                logger.error('Error API answer!')
                message = 'Адрес Практикума недоступен!'
                if message != message_repeat:
                    message_repeat = message
                    try:
                        send_message(bot, message)
                        logger.info(f'Message {message} send to Telegram.')
                    except telegram.TelegramError:
                        logger.error('Error send message to Telegram!')
                raise
            try:
                homeworks = check_response(response)
            except Exception:
                logger.error('Error check_response!')
                message = 'Домашка не найдена или с ней проблемы!'
                if message != message_repeat:
                    message_repeat = message
                    try:
                        send_message(bot, message)
                        logger.info(f'Message {message} send to Telegram.')
                    except telegram.TelegramError:
                        logger.error('Error send message to Telegram!')
                raise
            homework = homeworks[0]
            try:
                message = parse_status(homework)
            except ValueError:
                logger.error('Error value in parse_status!')
                raise
            except ExceptionNonInspectedError:
                logger.error('Other Error in parse_status!')
                raise
            try:
                send_message(bot, message)
                logger.info(f'Message {message} send to Telegram.')
            except telegram.TelegramError:
                logger.error('Error send message to Telegram!')

            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            print(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
