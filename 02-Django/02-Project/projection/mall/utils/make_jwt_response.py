# coding=utf-8
from utils.user_serializer import to_serializer


def jwt_response_payload_handler(token, user=None, request=None):
    """jwt登陆验证后自定义返回数据"""
    return to_serializer(token, user)
