from flask_restful import Resource

from internal.postgres import category, channel, user
from pkg.log import logger


class UserResource:
    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self, id):
        """Метод GET для информации о пользователе

        :param id: ID пользователя в базе
        :type id: int
        :return: Информация о пользователе
        :rtype: JSON
        """
        res = self.user_storage.get_user_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

class UserListResource:
    def __init__(self,
                 logger: logger.Logger,
                 user_storage: user.UserStorage):
        self.logger = logger
        self.user_storage = user_storage

    def get(self):
        """Метод GET для списка пользователей

        :return: Список пользователей
        :rtype: JSON
        """
        user_res = []
        res = self.user_storage.get_all()
        for item in res:
            user_res.append(item.to_json())
        
        return user_res, 200
