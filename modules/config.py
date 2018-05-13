class Config(object):
    DEBUG = False

class ProductionConfig(Config):
    MYSQL_PARAM = ["localhost", "root", "123456", "infox", "3306"]
    MONGO_PARAM = ["localhost", "27017"]
    COUCHBASE_PARAM = ["localhost", "general", "Administrator", "123456"]
    SESSION_PARAM = ["localhost", "session", "Administrator", "123456"]

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_PARAM = ["localhost", "root", "123456", "infox", "3306"]
    MONGO_PARAM = ["localhost", "27017"]
    COUCHBASE_PARAM = ["localhost", "general", "Administrator", "123456"]
    SESSION_PARAM = ["localhost", "session", "Administrator", "123456"]
    PROJECT_BASE = "/home/ghost/Desktop/Workshop/AnalyticsProject/infox-datashare"
    USER_BASE = "/static/user_base"

election = {
    "prod": ProductionConfig,
    "dev": DevelopmentConfig
}