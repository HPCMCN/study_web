import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask, g, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config.config import config_dict

db = SQLAlchemy()
redis_store = object


def create_redis_store(obj):
    global redis_store
    redis_store = obj


class Handle(object):
    """业务处理类"""
    redis_store = None

    def __init__(self, key):
        self.set_log()
        self.key = key
        self.create_app()

    def create_app(self):
        """创建app"""
        app = Flask(__name__)
        app = self.config(app)
        app = self.register(app)
        return app

    @staticmethod
    def set_log():
        """设置日志"""
        logging.basicConfig(level="DEBUG")
        log_file = RotatingFileHandler("logs/log.lg", maxBytes=1024 * 1024 * 100, backupCount=10, mode="rb")
        format_log = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s")
        log_file.setFormatter(format_log)
        logging.getLogger().addHandler(log_file)

    @staticmethod
    def register(app):
        """蓝图注册"""
        from .index import bp_index
        from .passport import bp_validate
        from .modules import models
        from .news import bp_new
        from .utils.common import filter_hot
        from user import bp_user, bp_admin
        app.register_blueprint(bp_index)
        app.register_blueprint(bp_validate)
        app.register_blueprint(bp_new)
        app.register_blueprint(bp_user)
        app.register_blueprint(bp_admin)
        # print(app.url_map)
        # 在这把规则添加到app中待用。
        app.add_template_filter(filter_hot)
        return app

    def config(self, app):
        """配置属性"""
        config = config_dict[self.key]
        app.config.from_object(config)
        obj = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
        create_redis_store(obj)
        Session(app)
        self.scrf_protect(app)
        db.init_app(app)

        from view.utils.common import is_user_login
        @app.errorhandler(404)
        @is_user_login
        def page_not_found(_):
            user = g.user
            data = {"user_info": user if user else None}
            return render_template('news/404.html', data=data)

        return app

    @staticmethod
    def scrf_protect(app):
        CSRFProtect(app)

        @app.after_request
        def after_request(response):
            csrf_token = generate_csrf()
            response.set_cookie("csrf_token", csrf_token)
            return response

        return app
