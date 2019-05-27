import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection

from cart.serializer import CartSerializer, CartSKUSerializer, CartDeleteSerializer
from contents.datail.content import LIVE_SAVE
from goods.models import SKU


# noinspection PyUnresolvedReferences
class CartsView(APIView):
    """购物车增删改查"""

    def is_login(self, request):
        try:
            user = request.user if request.user.is_authenticated else None
        except Exception:
            user = None
        return user

    def validate_obj(self, data):
        s = CartSerializer(data=data)
        s.is_valid(raise_exception=True)
        return s

    def get_data(self, s):

        sku_id = s.data.get("sku_id")
        count = s.data.get("count", None)
        selected = s.data.get("selected", None)
        return sku_id, int(count), selected

    def perform_authentication(self, request):
        """重写方法让签名过期和错误的数据进入视图函数"""
        pass

    def post(self, request):
        """
        添加数据
        post提交
        :param: id, count, selected
        """
        s = self.validate_obj(request.data)
        sku_id, count, selected = self.get_data(s)
        # 1. 登陆用户, 数据存储在redis
        if self.is_login(request):
            # 1. 登陆用户使用redis存储
            cur = get_redis_connection("cart")
            # 2. 使用管道符
            p1 = cur.pipeline()
            # 3. 添加并且修改数据
            p1.hincrby("cart_%s" % request.user.id, sku_id, count)
            if selected:
                # 如果选中, 就将当前的商品id添加到列表中
                p1.sadd("cart_selected_%s" % request.user.id, sku_id)
            p1.execute()
            return Response(s.data)
        # 2. 未登录用户, 数据存储在cookie中
        cart_str = request.COOKIES.get("cart", None)
        # 1. 判断是否为空, 如果有数据需要解码
        cart_dict = pickle.loads(base64.b64decode(cart_str)) if cart_str else {}
        # 2. 如果有相同的商品, 进行累加:
        if sku_id in cart_dict:
            # 从cookie中取出count进行累加
            count_save = cart_dict.get(sku_id).get("count")
            count += int(count_save)
        # 3. 重新配置数据
        cart_dict[sku_id] = {
            "count": count,
            "selected": selected
        }

        response = Response(s.data)
        # 4. 编码发送
        encode_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()
        response.set_cookie("cart", encode_cart, LIVE_SAVE)

        return response

    def get(self, request):
        """
        获取购物车数据
        :param:
        """
        # 1. 判断用户是否登陆
        if self.is_login(request):
            # 1. 连接redis
            cur = get_redis_connection("cart")
            # 2. 获取全部数据  sku_id, count, selected
            redis_cart = cur.hgetall("cart_%s" % request.user.id)
            redis_selected_ids = cur.smembers("cart_selected_%s" % request.user.id)
            # 3. 组织数据, 对数据进行字典推导式添加数据
            cart = {int(sku_id): {"count": int(count), "selected": sku_id in redis_selected_ids}
                    for sku_id, count in redis_cart.items()}
        # 2. 没有登陆的用户
        else:
            # 1. 从cookie中获取数据
            cart_str = request.COOKIES.get("cart", None)
            # 2. 判断cart_str是否为空, 如果存在获取并解码
            cart = pickle.loads(base64.b64decode(cart_str.encode())) if cart_str else {}
        # 3. 模块查询列表中的所有中商品
        skus = SKU.objects.filter(id__in=cart.keys())
        # 4. 遍历出来每一项准备序列化:
        # skus = [setattr(sku, "count", cart[sku.id]["count"]) and setattr(sku, "selected", cart[sku.id]['selected'])
        #  for sku in skus_byte]
        for sku in skus:
            setattr(sku, "count", cart[sku.id]["count"])
            setattr(sku, "selected", cart[sku.id]['selected'])

        # 5. 序列化数据
        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        """
        :param: sku_id, count, selected
        # 这里使用幂等, 进行数据修改
        """
        s = self.validate_obj(request.data)
        sku_id, count, selected = self.get_data(s)
        # 1. 登陆用户
        if self.is_login(request):
            # 获取redis中的数据
            cur = get_redis_connection("cart")
            p1 = cur.pipeline()
            p1.hset("cart_%s" % request.user.id, sku_id, count)
            if selected:
                p1.sadd("cart_selected_%s" % request.user.id, sku_id)
            else:
                p1.srem("cart_selected_%s" % request.user.id, sku_id)
            p1.execute()
            return Response(s.data)
        # 2. 未登录用户
        # 1. cookie获取并解码
        cart_str = request.COOKIES.get("cart", None)
        cart = pickle.loads(base64.b64decode(cart_str.encode())) if cart_str else {}
        if sku_id in cart:
            cart[sku_id] = {
                "count": count,
                "selected": selected
            }
        # 2. 数列化数据
        response = Response(s.data)
        # 3. 编码数据
        cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
        # 4. 设置cookie
        response.set_cookie("cart", cookie_cart, LIVE_SAVE)
        return response

    def delete(self, request):
        """
        :param: sku_id
        """
        s = CartDeleteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        sku_id = request.data.get("sku_id", None)
        # 1. 登陆用户
        if self.is_login(request):
            cur = get_redis_connection("cart")
            p1 = cur.pipeline()
            p1.hdel("cart_%s" % request.user.id, sku_id)
            p1.srem("cart_selected_%s" % request.user.id, sku_id)
            p1.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # 2. 未登录用户
        cart_str = request.COOKIES.get("cart", None)
        # 1. 解码
        cart = pickle.loads(base64.b64decode(cart_str.encode())) if cart_str else {}
        response = Response(status=status.HTTP_204_NO_CONTENT)
        if sku_id in cart:
            # 如果存在就删除
            cart.pop(sku_id)
            cookie_cart = base64.b64encode(pickle.dumps(cart_str)).decode()
            response.set_cookie("cart", cookie_cart, LIVE_SAVE)
        return response