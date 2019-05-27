# coding = utf-8
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderModel


class CartSKUSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    count = serializers.IntegerField()

    class Meta:
        model = SKU
        fields = ["id", "name", "default_image_url", "price", "count"]


class OrderSettlementSerializer(serializers.Serializer):
    """订单序列化器"""
    freight = serializers.DecimalField(max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


# noinspection PyUnreachableCode,PyUnboundLocalVariable,PyUnresolvedReferences
class OrderCommitSerializer(serializers.ModelSerializer):
    """生成订单序列化器"""
    class Meta:
        model = OrderModel
        fields = ["order_id", "pay_method", "address"]
        read_only_fields = ["order_id"]
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validate_data):
        """保存订单"""
        # 1. 获取当前下单用户
        user = self.context.get("request").user
        # 2. 生成订单编号
        order_code = timezone.now().strftime("%Y%m%d%H%M%S%f") + "%09d" % user.id
        # 3. 获取数据, 保存订单基本信息数据
        address = validate_data.get("address")
        pay_method = validate_data.get("pay_method")
        with transaction.atomic():
            # 创建还原点：
            old_save = transaction.savepoint()
            try:
                order = OrderModel.objects.create(
                    order_id=order_code,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal("0"),
                    pay_method=pay_method,
                    freight=Decimal("10.00"),
                    status=OrderModel.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderModel.PAY_METHODS_ENUM['CASH'] else
                    OrderModel.ORDER_STATUS_ENUM['UNPAID']
            )
                # 从redis中获取购物车结算商品数据
                cur = get_redis_connection("cart")
                cart_redis = cur.hgetall("cart_%s" % user.id)
                cart_selected = cur.smembers("cart_selected_%s" % user.id)
                cart = {int(sku_id): int(cart_redis[sku_id]) for sku_id in cart_selected}
                # 遍历结算商品：
                for sku_id in cart.keys():
                    for i in range(10):
                        sku = SKU.objects.get(pk=sku_id)
                        count = cart[sku.id]
                        if count > sku.stock:
                            # 判断商品库存是否充足
                            transaction.savepoint_rollback(old_save)
                            raise serializers.ValidationError("库存不足！")
                        # 减少商品库存，增加商品销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        new_stock = origin_stock - count
                        new_sales = origin_sales + count
                        result = SKU.objects.filter(id=sku.id, stock=origin_stock).update(
                            stock=new_stock, sales=new_sales)
                        if result == 0:
                            continue
                        # sku.stock -= count
                        # sku.sales += count
                        # sku.save()
                        # 商品个数
                        order.total_count += count
                        # 商品总价
                        order.total_amount += sku.price * count
                        break
                    # 保存订单商品数据
                    if result == 0:
                        raise serializers.ValidationError("%s下单超时, 请重试!" % sku.name)
                order.save()
            except Exception:
                transaction.savepoint_rollback(old_save)
                raise serializers.ValidationError("下单失败!")
                return
            else:
                transaction.savepoint_commit(old_save)
            # 在redis购物车中删除已计算商品数据
            p1 = cur.pipeline()
            p1.hdel("cart_%s" % user.id, *cart_selected)
            p1.srem("cart_selected_%s" % user.id, *cart_selected)
            p1.execute()
            return order


