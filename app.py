import toml
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from Telemetr_app.handlers.api import UserResource
from Telemetr_app.internal.postgres import postgres, user
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

api.add_resource(UserResource, "/api/v1/user",
                 resource_class_args=(logger, user_storage, ))

if __name__ == "__main__":
    app.run(debug=cfg.get("run").get("debug"),
            port=cfg.get("run").get("port"))
