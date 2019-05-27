# coding=utf-8
import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


class UserValidateBackend(ModelBackend):
    """用户登陆验证"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """验证"""
        # 1 判断是手机号还是用户名登陆
        login_name = self.get_name(username)
        # 2 校验密码
        if login_name is not None and login_name.check_password(password):
            return login_name
        return None

    @staticmethod
    def get_name(account):
        """判断用户名"""
        try:
            if re.match(r"1[356789]{9}", account):
                user = User.objects.get(mobile=account)
            else:
                user = User.objects.get(username=account)
        except User.DoesNotExist:
            return None
        return user
