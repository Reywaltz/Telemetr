from abc import ABC, abstractmethod


class Logger(ABC):
    """Абстрактный класс логгера"""
    @abstractmethod
    def info(self, msg: str):
        """Логирование информационных сообщений

        :param msg: Сообщение
        :type msg: str
        """
        pass

    def warning(self, msg: str):
        """Логирование сообщений предупреждений

        :param msg: Сообщение
        :type msg: str
        """
        pass

    def error(self, msg: str):
        """Логирование сообщений ошибок

        :param msg: Сообщение
        :type msg: str
        """
        pass

    def critical(self, msg: str):
        """Логирование сообщений критических ошибок

        :param msg: Сообщение
        :type msg: str
        """
        pass
