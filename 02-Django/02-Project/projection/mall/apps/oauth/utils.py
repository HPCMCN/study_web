# coding=utf-8
import json
from urllib import parse
from urllib.parse import parse_qs
from urllib.request import urlopen

from rest_framework.response import Response

from contents.login.tencent import *


class LoginInteraction(object):
    """登陆三方数据交互"""

    def __init__(self):
        self.base_url = ""
        self.data = None
        self.access = None
        self.params_dict = {
            "get_qq_code_id": self.get_qq_code_id,
            "get_wx_code_id": self.get_wx_code_id,
            "get_qq_token": self.get_qq_token,
            "get_qq_open_id": self.get_qq_open_id
        }

    def join_url(self, key_or_dict=None):
        """将url与参数拼接"""

        param_dict = key_or_dict if self.base_url else self.dispatch(key_or_dict)

        return self.base_url + parse.urlencode(param_dict)

    def get_url_data(self, access=None, token=None):
        """数据交互"""
        # 1. 获取对应参数
        param_dict = self.dispatch(access, token)
        # 2. 数据拼接到url中
        url = self.join_url(param_dict)
        # 3. 访问获取数据
        self.data = self.access_url(url)
        # 4. 处理并返回数据
        self.base_url = None
        return self.handle_data()

    @staticmethod
    def access_url(url=None):
        """访问url"""
        return urlopen(url)

    @staticmethod
    def send_url(url):
        return Response({"auth_url": url})

    def handle_data(self):

        data_str = self.data.read().decode()
        data_dict = parse_qs(data_str) or json.loads(data_str[10:-4])

        return data_dict

    def dispatch(self, key, value=None):

        self.access = key

        param_dict = self.params_dict[key]

        if key == "get_qq_code_id":
            self.base_url = GET_QQ_CODE_ID_URL

        elif key == "get_qq_token":
            param_dict["code"] = value
            self.base_url = GET_QQ_TOKEN_URL

        elif key == "get_qq_open_id":
            param_dict["access_token"] = value.get("access_token")[0]
            self.base_url = GET_QQ_OPEN_ID_URL

        elif key == "get_wx_code_id":
            self.base_url = GET_WECHAT_CODE_ID_URL

        elif key == "get_wx_token":
            param_dict["code"] = value
            self.base_url = GET_WECHAT_TOKEN_URL

        return param_dict

    get_qq_code_id = {
        "response_type": "code",
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URL,
        "state": "/",
        "scope": "get_user_info"
    }

    get_qq_token = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": APP_KEY,
        "redirect_uri": REDIRECT_URL
    }

    get_qq_open_id = {}

    get_wx_code_id = {
        "appid": APP_ID,
        "redirect_uri": REDIRECT_URL,
        "response_type": "code",
        "scope": "snsapi_login",
        "state": "/",
    }

    get_wx_token = {
        "appid": APP_ID,
        "secret": APP_KEY,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URL
    }

    def __enter__(self):
        # self.local = Local()
        self.local = LoginInteraction()
        # setattr(self.local, "a", LoginInteraction())
        # return self.local.a
        return self.local

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.local
        global link_tx
        link_tx = None
        return False


link_tx = LoginInteraction()

# def first(get_response):
#     link_tx = LoginInteraction()
#     def link_tx_create(request):
#
#         global link_tx
#         with LoginInteraction() as link_tx:
#             print(2222)
#             print(threading.current_thread().name)
#             response = get_response(request)
#
#             return response
#
#     return link_tx_create
