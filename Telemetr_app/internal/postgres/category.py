from dataclasses import dataclass
from typing import List

from Telemetr_app.internal.categories import category
from Telemetr_app.internal.postgres import postgres


@dataclass
class CategoryStorage(category.Storage):
    """Реализация абстрактного класса Storage категорий

    :param user: абстрактный класс категорий
    :type user: category.Storage
    """
    db: postgres.DB

    get_categories_query = "SELECT * FROM categories ORDER BY name"

    def get_all(self) -> List[category.Category]:
        """Метод получения всех категорий из БД

        :return: Категории из БД
        :rtype: List[Category]
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_categories_query)
        row = cursor.fetchall()
        ch_list = scan_categories(row)

        return ch_list

    def create(self, category):
        pass


def scan_category(data: tuple) -> category.Category:
    """Преобразование SQL ответа в объект

    :param data: SQL ответ
    :type data: tuple
    :return: Объект категории
    :rtype: Category
    """
    return category.Category(
        name=data[0]
    )


def scan_categories(data: List[tuple]) -> List[category.Category]:
    """Функция преобразовния SQL ответа в список объектов Categories

    :param data: SQL ответ из базы
    :type data: List[tupple]
    :return: Список категорий
    :rtype: List[Category]
    """
    categories = []
    for row in data:
        category = scan_category(row)
        categories.append(category)

    return categories


def new_storage(db: postgres.DB) -> CategoryStorage:
    """Функция инициализации хранилища категорий

    :param db: объект базы данных
    :type db: postgres.DB
    :return: объект хранилища категорий
    :rtype: Category
    """
    return CategoryStorage(db=db)
