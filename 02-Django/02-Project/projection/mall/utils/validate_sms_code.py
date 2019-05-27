# coding=utf-8
from django_redis import get_redis_connection


def get_redis_sms_code(mobile):
    """获取正确验证码"""
    cur = get_redis_connection("code")
    code = cur.get("sms_code_%s" % mobile)
    cur.delete("sms_code_%s" % mobile)
    return code


def validate_sms_code(sms_code_test, mobile):
    """验证短信验证码"""
    sms_code = get_redis_sms_code(mobile)
    if not sms_code:
        return "验证码过期!"
    if sms_code.decode() != sms_code_test:
        return "验证码错误!"
    return True
