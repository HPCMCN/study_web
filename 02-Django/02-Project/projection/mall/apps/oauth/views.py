from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.Serializers import OAuthUserSerializers
from oauth.models import OAuthQQUser
from oauth.utils import link_tx
from utils.token_itsdangerous import token_encode
from utils.user_serializer import to_serializer
from utils.token_JWT import make_token


class QQRegisterView(APIView):
    """qq登陆认证"""
    # 1. 前端提供: 手机号, 密码, 短信验证码, token四个参数
    # 2. 使用序列化器进行验证
    # 3. 将验证通过的data进行保存
    # 4. 将token发送给客户端实现登陆状态
    @staticmethod
    def post(request):

        serializer = OAuthUserSerializers(data=request.data)
        serializer.is_valid()
        data = serializer.save()

        return Response(data)


# noinspection PyUnusedLocal
class OauthQQView(APIView):
    """创建qq连接视图"""

    @staticmethod
    def get(request):
        # 将qq的url发给用户, 实现三方登陆
        url = link_tx.join_url("get_qq_code_id")
        return Response({"auth_url": url})


class OauthQQUserView(APIView):
    """与qq服务器交互"""

    @staticmethod
    def get(request):
        # 1. 从客户端拿到code
        code = request.query_params.get("code")

        if code is None:
            return Response(status=400)

        # 2. 利用code访问qq获取token
        token_data = link_tx.get_url_data("get_qq_token", code)
        # 'callback( {"client_id":"101474184","openid":"3FCC18185E46F988D464CF0AC5CB9676"} );

        # 3. 利用token访问qq获取open_id
        open_id_data = link_tx.get_url_data("get_qq_open_id", token_data)

        openid = open_id_data.get("openid")

        try:
            # 首先获取openid, 如果获取成功说明已经存在, 直接登陆即可
            user_openid = OAuthQQUser.objects.get(openid=openid)
            # 关联获取到user
            user = user_openid.user
        except OAuthQQUser.DoesNotExist:
            # 加密open_id, 返回token, 进入注册页面
            token = token_encode({"openid": openid})
            return Response({"access_token": token})

        # 生成token
        token = make_token(user)
        # 序列化数据token, id, username
        data = to_serializer(token, user)
        # 返回, 登陆成功
        return Response(data)


# class WeChatView(APIView):
#     """获取微信接口"""
#
#     @staticmethod
#     def get(request):
#         """拼接url发给客户端实现三方登陆"""
#         url = link_tx.join_url("get_wx_code_id")
#         return link_tx.send_url(url)
#
#
# class WeChatUserView(APIView):
#     """与微信服务器交互"""
#
#     @staticmethod
#     def get(request):
#         code = request.query_params.get("code")
#
#         get_token_url = link_tx.get_url_data("get_wx_token")
#         pass
