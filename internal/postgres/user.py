from dataclasses import dataclass
from typing import List

from internal.postgres import postgres
from internal.users import user


@dataclass
class UserStorage(user.Storage):
    """Реализация абстрактного класса Storage пользователя

    :param user: абстрактный класс пользователя
    :type user: Storage
    """
    db: postgres.DB

    get_users_query = "SELECT * FROM users"

    get_user_query = "SELECT * FROM users WHERE id = %s ORDER BY id"

    def create(self, user: user.User):
        """Метод добавления нового пользователя

        :param user: [description]
        :type user: User
        """
        pass

    def get_all(self) -> List[user.User]:
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

        :param id: ID пользователя
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


def scan_user(data: tuple) -> user.User:
    """Преобразование SQL ответа в объект

    :param data: SQL ответ
    :type data: tuple
    :return: Объект пользователя
    :rtype: Users
    """
    return user.User(
        id=data[0],
        username=data[1],
    )


def scan_users(data: List[tuple]) -> List[user.User]:
    """Функция преобразования SQL ответа в список объектов Users

    :param data: SQL ответ
    :type data: List[tupple],
    :return: Список объектов пользователей
    :rtype: List[User]
    """
    users = []
    for row in data:
        user = scan_user(row)
        users.append(user)

    return users


def new_storage(db: postgres.DB) -> UserStorage:
    """Функция инициализации хранилища пользователей

    :param db: объект базы данных
    :type db: postgres.DB
    :return: объект хранилища продуктов
    :rtype: User
    """
    return UserStorage(db=db)
