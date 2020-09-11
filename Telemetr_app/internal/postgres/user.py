from dataclasses import dataclass
from typing import List

from Telemetr_app.internal.postgres import postgres
from Telemetr_app.internal.users import user


@dataclass
class UserStorage(user.Storage):
    """Реализация абстрактного класса Storage пользователя

    :param user: абстрактный класс пользователя
    :type user: user.Storage
    """
    db: postgres.DB

    get_users_query = "SELECT * FROM USERS"

    def insert(self, user: user.User):
        """Метод добавления нового пользователя

        :param user: [description]
        :type user: user.User
        """
        pass

    def get_all(self) -> List[user.User]:
        """Метод получения всех пользователей в базе данных

        :return: Список пользователей
        :rtype: user.User
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_users_query)
        row = cursor.fetchall()
        print(row)
        u = scan_users(row)

        return u

    def find_user_by_id(self, id):
        pass


def scan_user(data) -> user.User:
    """Преобразование SQL ответа в объект

    :param data: SQL ответ
    :type data: tupple
    :return: Объект пользователя
    :rtype: user.Users
    """
    return user.User(
        id=data[0],
        username=data[1],
    )


def scan_users(data):
    """Функция преобразования SQL ответа в список объектов Users

    :param data: SQL ответ
    :type data: List[tupple],
    :return: Список объектов пользователей
    :rtype: List[user.User]
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
    :rtype: user.User
    """
    return UserStorage(db=db)
