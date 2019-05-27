# coding=utf-8


import logging

from django_redis import get_redis_connection
from redis.exceptions import RedisError
from rest_framework import serializers
from rest_framework.response import Response

logger = logging.getLogger("running")


class RegisterSMSCodeSerializer(serializers.Serializer):
    """发送短信验证器"""

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    # 1. 确定验证字段为： UUID, image_code, 手机验证在url中用正则进行匹配
    # 2. 自带验证器不能满足规则, 需要另外添加规则
    # 3. 注意验证器的执行顺序为： 字段->字段参数->单字段->多字段
    # 4. 从attr中取出字段验证后的数据, 连接redis取出image_code并删除数据库对应数据(try)
    # 5. 验证是否过期, 是否相同(注意redis中取出的为二进制, 需要适配大小写)
    # 6. 返回attr
    image_code_id = serializers.UUIDField(required=True)
    text = serializers.CharField(max_length=4, min_length=4, required=True)

    def validate(self, attr):
        uuid = attr.get("image_code_id")
        image_code_test = attr.get("text")
        cur = get_redis_connection("code")
        image_code = cur.get("image_code_%s" % uuid)
        try:
            cur.delete("image_code_%s" % uuid)
        except RedisError as e:
            logger.error(e)
        if not image_code:
            raise RedisError("验证码已过期！")
        if image_code.decode().lower() != image_code_test.lower():
            return Response("验证码错误！", status=400)
        return attr
