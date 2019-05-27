from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, OrderCommitSerializer


class OrderSettlementView(APIView):
    """获取订单"""
    def get(self, request):
        """订单生成get请求"""
        user = request.user
        # 1. 前端需要提供: PayMethod, 收货地址等数据
        cur = get_redis_connection("cart")
        cart_redis = cur.hgetall("cart_%s" % user.id)
        cart_selected = cur.smembers("cart_selected_%s" % user.id)
        # 2. 获取出选中的redis中所需的商品和数量
        cart = {int(sku_id): int(cart_redis[sku_id]) for sku_id in cart_selected}
        # 3. 查询出商品信息：
        skus = SKU.objects.filter(id__in=cart.keys())
        # 4. 向sku中添加count准备序列化
        for sku in skus:
            setattr(sku, "count", cart[sku.id])
        # 5. 获取运费数据：
        freight = Decimal("10.00")
        # 6. 序列化数据：
        serializer = OrderSettlementSerializer({"freight": freight, "skus": skus})
        return Response(serializer.data)


class OrderCreateView(CreateAPIView):
    """保存订单"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCommitSerializer



