from dataclasses import dataclass

from internal.categories import category
from internal.postgres import postgres
from pkg.log import logger
from psycopg2 import IntegrityError

category_fields = "name"


@dataclass
class CategoryStorage(category.Storage):
    """Реализация абстрактного класса Storage категорий"""

    db: postgres.DB
    logger: logger.Logger

    get_categories_query = "SELECT name FROM categories ORDER BY name"

    insert_category_query = "INSERT INTO categories (" + category_fields + \
                            " ) VALUES (%s)"

    def get_all(self) -> list[category.Category]:
        """Метод получения всех категорий из БД

        :return: Категории из БД
        :rtype: list[Category]
        """
        cursor = self.db.session.cursor()
        cursor.execute(self.get_categories_query)
        row = cursor.fetchall()
        ch_list = scan_categories(row)

        return ch_list

    def insert(self, category: category.Category) -> bool:
        """Метод добавления новой категории в БД

        :param category:
            Объект категории
            :type category: category.Category
        :return: Результат вставки
        :rtype: bool
        """
        try:
            cursor = self.db.session.cursor()
            cursor.execute(self.insert_category_query, (category.name, ))
            self.db.session.commit()
            self.logger.info(f"Добавлена категория: {category.name}")
            return True
        except IntegrityError:
            self.db.session.rollback()
            self.logger.error(f"Ошибка при добавлении категории {category.name}. Такая категория уже существует") # noqa
            return False


def scan_category(data: tuple) -> category.Category:
    """Преобразование SQL ответа в объект

    :param data:
        SQL ответ
        :type data: tuple
    :return: Объект категории
    :rtype: Category
    """
    return category.Category(
        name=data[0]
    )


def scan_categories(data: list[tuple]) -> list[category.Category]:
    """Функция преобразовния SQL ответа в список объектов Categories

    :param data:
        SQL ответ из базы
        :type data: list[tupple]
    :return: Список категорий
    :rtype: list[Category]
    """
    categories = []
    for row in data:
        category = scan_category(row)
        categories.append(category)

    return categories


def new_storage(db: postgres.DB, logger: logger.Logger) -> CategoryStorage:
    """Функция инициализации хранилища категорий

    :param db:
        объект базы данных
        :type db: postgres.DB
    :return: объект хранилища категорий
    :rtype: Category
    """
    return CategoryStorage(db=db, logger=logger)
