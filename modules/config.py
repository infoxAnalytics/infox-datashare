class Config(object):
    DEBUG = False
    USER_BASE = "/static/user_base"
    LOGGING_BASE = "/var/log/infox-analytics"
    LOG_LEVEL = "INFO"


class ProductionConfig(Config):
    MYSQL_PARAM = ["localhost", "root", "123456", "infox", "3306"]
    MONGO_PARAM = ["localhost", "27017", "superAdmin", "123456", "admin", "SCRAM-SHA-1"]
    COUCHBASE_PARAM = ["localhost", "general", "Administrator", "123456"]
    SESSION_PARAM = ["localhost", "session", "Administrator", "123456"]
    PROJECT_BASE = "/usr/share/nginx/html/infox-datashare"


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_PARAM = ["localhost", "root", "123456", "infox", "3306"]
    MONGO_PARAM = ["localhost", "27017", "superAdmin", "123456", "admin", "SCRAM-SHA-1"]
    COUCHBASE_PARAM = ["localhost", "general", "Administrator", "123456"]
    SESSION_PARAM = ["localhost", "session", "Administrator", "123456"]
    PROJECT_BASE = "/home/ghost/Desktop/Workshop/AnalyticsProject/infox-datashare"
    CHANGESET_FILE = "/modules/dbchangelog/changelog_ver-1_0.json"


election = {
    "prod": ProductionConfig,
    "dev": DevelopmentConfig
}
