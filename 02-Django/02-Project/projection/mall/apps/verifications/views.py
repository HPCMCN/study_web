from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.captcha.captcha import captcha
from verifications.serializer import RegisterSMSCodeSerializer


class ImageCodeAPIView(APIView):
    """生成图片验证码"""

    # 1. 前端通过URL提供UUID
    # 2. 调用模块生成图片和验证码
    # 3. 调用redis储存验证码, 并设置有效期60s
    # 4. 返回给客户端Image, 注意设置格式content-type
    @staticmethod
    def get(request, image_code_id):
        text, image = captcha.captcha.generate_captcha()
        print(request)
        print(text)
        text = "1111"
        cur = get_redis_connection("code")

        cur.setex("image_code_%s" % image_code_id, 60, text)
        return HttpResponse(image, content_type="image/jpeg")
        # return Response(image, content_type="image/jpeg")


# 1. 前端提供UUID, 手机号, 图片验证码
# 2. 利用验证器验证UUID/手机号/图片验证码的合法性, 并验证图片验证码的正确性
# 3. 验证该用户是否在频繁操作：
# 将手机号存入redis中, 生命周期是60s, 每次发送短信之前首先进行get
# 判断是否能get出来数据, 如果有说明频繁获取
# 4. 异步制作短信验证码
# 5. 返回发送成功！

class RegisterSMSCodeView(GenericAPIView):
    """短信验证码发送验证"""
    serializer_class = RegisterSMSCodeSerializer

    def get(self, request, mobile):
        # 获取序列化器, 验证数据
        ser = self.get_serializer(data=request.query_params)
        ser.is_valid(raise_exception=True)

        # 连接redis, 判断是否为一个手机号频繁访问
        cur = get_redis_connection("code")
        if cur.get("is_re_%s" % mobile):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 生成短信验证码
        import random
        sms_code = "%06d" % random.randint(0, 999999)
        sms_code = "111111"

        # 异步添加数据
        from celery_tasks.tasks.sms_send import send_sms_code
        send_sms_code.delay(mobile, sms_code)
        print(sms_code)

        # 存储短信验证码
        cur.setex("sms_code_%s" % mobile, 5 * 60, sms_code)

        # 向redis中添加该手机号确保恶意访问
        cur.setex("is_re_%s" % mobile, 60, 1)
        return JsonResponse({"status": 200})
