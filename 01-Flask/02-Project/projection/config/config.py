import redis


class Config(object):
    """通用配置"""
    # 全局配置
    SECRET_KEY = "hello_world"
    HOST = "0.0.0.0"

    # mysql配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:dong10@localhost:3306/db_information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

    # session配置
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USER_SIGNER = True
    PERMANENT_SESSION_LIFTTIME = 60 * 60 * 24 * 30


class DevelopmentConfig(Config):
    """开发模式配置"""
    DEBUG = True


class ProductionConfig(Config):
    """上线配置"""
    DEBUG = False


# 创建快捷通道
config_dict = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
