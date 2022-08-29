class BotException(Exception):
    """Ошибки бота."""


class ExceptionNot200Error(BotException):
    """Запрос не вернул ответ с кодом 200."""


class ExceptionTelegram(BotException):
    """Сообщение не отправилось в чат."""


class ExceptionResponseError(BotException):
    """Ошибка отклика."""


class ExceptionListEmpty(BotException):
    """Ошибка списка домашних работ."""


class ExceptionStatusUnknown(KeyError):
    """Неизвестный статус домашней работы."""

class ExceptionNonInspectedError(BotException):
    """Прочие ошибки."""
