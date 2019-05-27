# coding=utf-8
import re

from rest_framework import serializers

from celery_tasks.tasks.email_send import send_verify_email
from users.models import User, Address
from utils.token_JWT import make_token
from utils.token_itsdangerous import token_encode
from utils.validate_sms_code import validate_sms_code


# noinspection SpellCheckingInspection
class UserSerializer(serializers.ModelSerializer):
    """用户表单序列化器"""
    allow = serializers.CharField(write_only=True, allow_blank=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True, allow_blank=True)
    password2 = serializers.CharField(min_length=8, max_length=21, write_only=True, allow_blank=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "mobile",
                  "password2", "allow", "sms_code",
                  "token", "id", "email_active")
        extra_kwargs = {
            "id": {"read_only": True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        password1 = attrs.get("password")
        password2 = attrs.get("password2")
        mobile = attrs.get("mobile")
        allow = attrs.get("allow")
        sms_code_test = attrs.get("sms_code")

        if password1 != password2:
            raise serializers.ValidationError("两次输入密码不一致！")

        if not re.match(r"^1[356789]\d{9}$", mobile):
            raise serializers.ValidationError("手机号不合法！")

        if not allow:
            raise serializers.ValidationError("请勾选用户协议！")

        sms_validate = validate_sms_code(sms_code_test, mobile)
        if sms_validate is not True:
            raise serializers.ValidationError(sms_validate)

        return attrs

    def create(self, attrs):
        attrs.pop("password2")
        attrs.pop("allow")
        attrs.pop("sms_code")
        print(attrs.get("password"))

        user = User().ser_dict(attrs)

        user.save()

        # 给user制作token, 并赋值
        user.token = make_token(user)

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """个人中心序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """邮箱认证序列化器"""

    class Meta:
        model = User
        fields = ["email", "id"]
        extra_kwargs = {
            "email": {
                "required": True
            }
        }

    def update(self, obj, data):
        email = obj.email
        if not email:
            email = data.get("email")
            obj.email = email
            obj.save()
            print("用户邮箱绑定成功!")
        token = token_encode({"id": obj.id, "email": email})
        send_verify_email.delay(email, token)
        print("激活邮件发送成功!", email)
        return obj


class AddressSerializer(serializers.ModelSerializer):
    """收货地址"""
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validate_data):
        """创建收货地址"""
        # 从context中获取request.user
        user = self.context.get("request").user
        # 将user添加到验证后的数据中, 绑定外键
        validate_data["user"] = user
        return super().create(validate_data)


from goods.models import SKU
from django_redis import get_redis_connection


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览记录序列化器
    """
    sku_id = serializers.IntegerField(label='商品编号', min_value=1, required=True)

    def validate_sku_id(self, value):
        """
        检查商品是否存在
        """
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    def create(self, validated_data):

        # 获取用户信息
        user_id = self.context['request'].user.id
        # 获取商品id
        sku_id = validated_data['sku_id']
        # 连接redis
        redis_conn = get_redis_connection('history')
        # 移除已经存在的本记录
        redis_conn.lrem('history_%s' % user_id, 0, sku_id)
        # 添加新的记录
        redis_conn.lpush('history_%s' % user_id, sku_id)
        # 保存最多5条记录
        redis_conn.ltrim('history_%s' % user_id, 0, 4)
        return validated_data


from rest_framework import serializers
from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
