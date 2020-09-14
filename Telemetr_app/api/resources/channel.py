from flask_restful import Resource
from Telemetr_app.internal.postgres import user, channel, category
from Telemetr_app.pkg.log import logger

class ChannelResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 channel_storage: channel.ChannelStorage):
        self.logger = logger
        self.channel_storage = channel_storage

    def get(self, id):
        """Метод GET для информации о канале

        :param id: ID канала в базе
        :type id: int
        :return: Информация о канале
        :rtype: JSON
        """
        res = self.channel_storage.get_channel_by_id(id)
        if res is not None:
            return res.to_json(), 200
        else:
            return {"error": "not found"}, 404

class ChannelListResource(Resource):
    def __init__(self,
                 logger: logger.Logger,
                 channel_storage: channel.ChannelStorage):
        self.logger = logger
        self.channel_storage = channel_storage

    def get(self):
        """Метод GET для списка каналов

        :return: Список каналов
        :rtype: JSON
        """
        channel_res = []
        res = self.channel_storage.get_all()
        for item in res:
            channel_res.append(item.to_json())

        return channel_res, 200