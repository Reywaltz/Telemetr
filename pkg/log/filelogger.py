import logging
import os
from pkg.log.logger import Logger


class STDLogger(Logger):
    """Класс файлового логгера

    :param Logger:
        Абстрактный класс
        :type Logger: ABC
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)


def new_logger(logger_name: str) -> STDLogger:
    """Создание нового логгера

    :param logger_name:
        Название логгера
        :type logger_name: str
    :return: новый логгер
    :rtype: logging.Logger
    """
    file_logger = logging.getLogger(logger_name)
    file_logger.setLevel(logging.DEBUG)
    if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
        os.mkdir('logs')
    fl = logging.FileHandler(f"logs/{logger_name}.log", encoding="UTF-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fl.setFormatter(formatter)
    file_logger.addHandler(fl)

    logger = STDLogger(file_logger)
    return logger
