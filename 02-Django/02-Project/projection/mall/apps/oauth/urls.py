# coding=utf-8
from django.conf.urls import url

from oauth.views import *

urlpatterns = [
    url(r"^qq/statues/$", OauthQQView.as_view(), name="qq_statues"),
    url(r"^qq/users/$", OauthQQUserView.as_view(), name="qq_user"),
    url(r"^register_users/$", QQRegisterView.as_view(), name="register_user"),
    # url(r"^wechat/statues/$", WeChatView.as_view(), name="wechat_statues"),
    # url(r"^wechat/users/$", WeChatUserView.as_view(), name="wechat_user"),
]


