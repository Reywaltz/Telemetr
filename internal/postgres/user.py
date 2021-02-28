from dataclasses import dataclass

from internal.postgres import postgres
from internal.users import user
from pkg.log import logger
from psycopg2.errors import UniqueViolation

insert_user_field = "username, telegram_id, auth_code, created_at, valid_to"


@dataclass
class UserStorage(user.Storage):
    """Реализация абстрактного класса Storage пользователя"""

    db: postgres.DB
    logger: logger.Logger

    get_users_query = "SELECT * FROM users"

    get_users_by_auth_code_query = "SELECT * FROM users WHERE auth_code = %s"

    get_user_query = "SELECT * FROM users WHERE id = %s ORDER BY id"

    insert_user_query = "INSERT INTO users ( " + insert_user_field + ") \
                        VALUES (%s, %s, %s, %s, %s)"

    update_auth_key_query = "UPDATE users SET auth_code=%s, valid_to=%s \
                            WHERE telegram_id='%s' RETURNING id"

    def create(self, user: user.User):
        """Метод добавления нового пользователя

        :param user:
            Объект пользователя
            :type user: User
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(self.insert_user_query, (user.username,
                                                    user.telegram_id,
                                                    user.auth_code,
                                                    user.created_at,
                                                    user.valid_to))
            self.db.session.commit()
            return True
        except UniqueViolation:
            self.db.session.rollback()
            self.logger.info(f"Пользователь под ID:{user.id} уже существует")
            return False
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"Ошибка при создании пользователя - {e}")
            return False

    def get_all(self) -> list[user.User]:
        """Метод получения всех пользователей в базе данных

        :return: Список пользователей
        :rtype: User
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_users_query)
        row = cursor.fetchall()
        u = scan_users(row)

        return u

    def get_user_by_id(self, id: int) -> user.User:
        """Метод получения пользователя в базе данных

        :param id:
            ID пользователя
            :type id: int
        :return: Пользователь из БД
        :rtype: User
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_user_query, (id, ))
        row = cursor.fetchone()
        if row is not None:
            return scan_user(row)
        else:
            return None

    def get_user_by_authcode(self, auth_code: str) -> user.User:
        """Метод проверки авторизации пользователя через телеграм бота

        :param auth_code:
            Сгенерированный код с клиента
            :type auth_code: str
        :return: Пользователя с данным кодом
        :rtype: user.User
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_users_by_auth_code_query, (auth_code, ))
        row = cursor.fetchone()
        if row is not None:
            return scan_user(row)
        else:
            return None

    def update_auth_key(self, user: user.User):
        """Метод обновления кода авторизации

        :param user:
            Объект пользователя
            :type user: user.User
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.update_auth_key_query, (user.auth_code,
                                                    user.valid_to,
                                                    user.telegram_id, ))
        row = cursor.fetchone()
        if row is not None:
            self.db.session.commit()
        else:
            self.db.session.rollback()


def scan_user(data: tuple) -> user.User:
    """Преобразование SQL ответа в объект

    :param data:
        SQL ответ
        :type data: tuple
    :return: Объект пользователя
    :rtype: Users
    """
    return user.User(
        id=data[0],
        username=data[1],
        telegram_id=data[2],
        auth_code=data[3],
        created_at=data[4],
        valid_to=data[5]
    )


def scan_users(data: list[tuple]) -> list[user.User]:
    """Функция преобразования SQL ответа в список объектов Users

    :param data:
        SQL ответ
        :type data: list[tupple],
    :return: Список объектов пользователей
    :rtype: list[User]
    """
    users = []
    for row in data:
        user = scan_user(row)
        users.append(user)

    return users


def new_storage(db: postgres.DB, logger: logger.Logger) -> UserStorage:
    """Функция инициализации хранилища пользователей

    :param db:
        объект базы данных
        :type db: postgres.DB
    :return: объект хранилища продуктов
    :rtype: User
    """
    return UserStorage(db=db, logger=logger)
