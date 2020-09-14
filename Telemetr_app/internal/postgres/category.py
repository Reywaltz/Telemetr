from dataclasses import dataclass
from Telemetr_app.internal.postgres import postgres
from Telemetr_app.internal.categories import category


@dataclass
class CategoryStorage(category.Storage):

    db: postgres.DB

    get_categories_query = "SELECT * FROM categories ORDER BY name"

    def get_all(self):
        cursor = self.db.session.cursor()
        cursor.execute(self.get_categories_query)
        row = cursor.fetchall()
        ch_list = scan_categories(row)

        return ch_list

    def create(self, category):
        pass


def scan_category(data):
    return category.Category(
        name=data[0]
    )


def scan_categories(data):
    """Функция преобразовния SQL ответа в список объектов Categories

    :param data: SQL ответ из базы
    :type data: List[tupple]
    :return: Список каналов
    :rtype: Channel[channel.Channel]
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
    :rtype: category.Category
    """
    return CategoryStorage(db=db)
