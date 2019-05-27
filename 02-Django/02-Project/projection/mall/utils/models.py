# coding=utf-8

from django.db import models


class BaseModel(models.Model):
    """补充创建时间/更新时间字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # 虚拟表, 不在数据库中创建
        abstract = True
