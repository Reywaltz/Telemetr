from datetime import datetime, timedelta
from psycopg2 import IntegrityError

from uuid import uuid4
import toml
from zoneinfo import ZoneInfo

from dataclasses import dataclass

from internal.admin import admin
from internal.postgres import postgres

cfg = toml.load("cfg.toml")
tz_info = cfg.get("timezone").get("tz_info")

tz = ZoneInfo(tz_info)

insert_admin_fields = 'username, password, access_token, created_at, \
                       valid_to'

admin_fields = "id, " + insert_admin_fields


@dataclass
class AdminStorage(admin.Storage):
    """Реализация абстрактного класса администратора"""

    db: postgres.DB

    get_admin_query = f"SELECT {admin_fields} FROM admin \
                                WHERE username = %s ORDER BY id"

    update_access_token_query = "UPDATE admin SET access_token=%s, \
                                created_at=%s, valid_to=%s WHERE username=%s"

    get_admin_by_token_query = f"SELECT {admin_fields} FROM admin \
                                WHERE access_token = %s"

    def get_admin(self, username: str) -> admin.Admin:
        """Метод получения администратора по юзернейму

        :return: Пользователя с токен
        :rtype: admin.Admin
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_admin_query, (username, ))
        row = cursor.fetchone()
        if row is None:
            return None

        return scan_admin(row)

    def update_token(self, admin: admin.Admin) -> str:
        """Метод обновления токена

        :param category:
            Объект категории
            :type category: admin.Admin
        :return: Результат вставки
        :rtype: bool
        """
        try:
            created_at = datetime.now(tz)
            valid_to = created_at + timedelta(hours=1)
            print(f"{created_at}, {valid_to} LESS? {created_at < valid_to}")
            access_token = str(uuid4())
            cursor = self.db.session.cursor()
            cursor.execute(self.update_access_token_query, (access_token,
                                                            created_at,
                                                            valid_to,
                                                            admin.username))
            self.db.session.commit()
            return access_token
        except IntegrityError:
            self.db.session.rollback()
            return None

    def get_admin_by_token(self, access_token: str) -> admin.Admin:
        """Метод проверки авторизации администратора
        :param access_token:
            Токен пришедший с клиента
            :type access_token: str
        :return: Администратора с токеном
        :rtype: admin.Admin
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_admin_by_token_query, (access_token, ))
        row = cursor.fetchone()
        if row is not None:
            return scan_admin(row)
        else:
            return None


def scan_admin(data: tuple) -> admin.Admin:
    """Преобразование SQL ответа в объект

    :param data:
        SQL ответ
        :type data: tuple
    :return: Объект администратора
    :rtype: Category
    """
    return admin.Admin(
        id=data[0],
        username=data[1],
        password=data[2],
        access_token=data[3],
        created_at=data[4],
        valid_to=data[5]
    )


def scan_admins(data: list[tuple]) -> list[admin.Admin]:
    """Функция преобразовния SQL ответа в список объектов Categories

    :param data:
        SQL ответ из базы
        :type data: list[tupple]
    :return: Список админов
    :rtype: list[Admin]
    """
    admins = []
    for row in data:
        admin = scan_admin(row)
        admins.append(admin)

    return admins


def new_storage(db: postgres.DB) -> AdminStorage:
    """Функция инициализации хранилища категорий

    :param db:
        объект базы данных
        :type db: postgres.DB
    :return: объект хранилища категорий
    :rtype: Category
    """
    return AdminStorage(db=db)
