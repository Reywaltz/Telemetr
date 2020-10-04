import psycopg2

from dataclasses import dataclass

from pkg.log import logger


@dataclass
class Config:
    """Класс конфигурации к бд"""
    database: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class DB:
    """Класс базы данных"""
    session: int
    logger: logger.Logger

    def close(self):
        self.session.close()


def new(cfg: Config, logger: logger.Logger) -> DB:
    """Создание нового подключения к базе данных

    :param cfg: параметры подключения к базе данных
    :type cfg: Config
    :param logger: логгер проекта
    :type logger: logger.Logger
    :return: объект подключения к базе данных
    :rtype: DB
    """
    conn = psycopg2.connect(
        database=cfg.database,
        user=cfg.user,
        password=cfg.password,
        host=cfg.host,
        port=cfg.port
    )
    db = DB(session=conn, logger=logger)
    return db
