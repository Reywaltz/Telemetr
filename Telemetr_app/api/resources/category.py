from flask_restful import Resource

from internal.postgres import category, channel, user
from pkg.log import logger


class CategoryListResource:
    def __init__(self,
                 logger: logger.Logger,
                 category_storage: category.CategoryStorage):
        self.logger = logger
        self.category_storage = category_storage

    def get(self):
        """Метод GET для информации о категориях

        :return: Список категорий в БД
        :rtype: JSON
        """
        category_res = []
        res = self.category_storage.get_all()
        for item in res:
            category_res.append(item.to_json())

        return category_res, 200
