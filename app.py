import toml
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from Telemetr_app.handlers.api import (CategoryListResource,
                                       ChannelListResource, ChannelResource,
                                       UserListResource, UserResource)
from Telemetr_app.internal.postgres import channel, postgres, user, category
from Telemetr_app.pkg.log import filelogger

cfg = toml.load("cfg.toml")


def configDB(cfg):
    cfgDB = postgres.Config(
        database=cfg.get("databases").get("database"),
        user=cfg.get("databases").get("user"),
        password=cfg.get("databases").get("password"),
        host=cfg.get("databases").get("host"),
        port=cfg.get("databases").get("port")
    )
    return cfgDB


logger = filelogger.new_logger("file_log")


app = Flask(__name__,
            instance_relative_config=cfg.get("secret_key").get("secret_key"))


CORS(app)
api = Api(app)

cfgDB = configDB(cfg)
db = postgres.new(cfg=cfgDB, logger=logger)
user_storage = user.new_storage(db)
channel_storage = channel.new_storage(db)
category_storage = category.new_storage(db)

api.add_resource(UserResource, "/api/v1/user/<int:id>",
                 resource_class_args=(logger, user_storage, ))

api.add_resource(UserListResource, "/api/v1/user",
                 resource_class_args=(logger, user_storage, ))                 

api.add_resource(ChannelResource, "/api/v1/channel/<int:id>",
                 resource_class_args=(logger, channel_storage, ))

api.add_resource(ChannelListResource, "/api/v1/channel",
                 resource_class_args=(logger, channel_storage, ))

api.add_resource(CategoryListResource, "/api/v1/category",
                 resource_class_args=(logger, category_storage, ))

if __name__ == "__main__":
    app.run(debug=cfg.get("run").get("debug"),
            port=cfg.get("run").get("port"))
