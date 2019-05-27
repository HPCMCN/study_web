# coding=utf-8
from celery import Celery


import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    # 添加Django的配置数据
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'


# 实例化Celery, 指明实例化的名字
app = Celery("celery_tasks")

# 加载配置文件
app.config_from_object("celery_tasks.config")

# 自动检测发送过来任务
app.autodiscover_tasks(["celery_tasks.tasks"])
