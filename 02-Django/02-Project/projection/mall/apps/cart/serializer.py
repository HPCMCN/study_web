# coding = utf-8
from rest_framework import serializers

from goods.models import SKU


# noinspection PyUnresolvedReferences,PyAbstractClass
class CartSerializer(serializers.Serializer):
    """创建数据提交的序列化器"""
    sku_id = serializers.IntegerField(required=True, min_value=1)
    count = serializers.IntegerField(required=True, min_value=1)
    selected = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        """校验所有字段"""
        # 1. 判断商品是否存在
        sku_id = attrs.get("sku_id")
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DestNotExist:
            raise serializers.ValidationError("商品不存在!")
        count = attrs.get("count")
        # 2. 判断库存
        if sku.stock < int(count):
            raise serializers.ValidationError("库存不足!")
        # 3. 防止恶意操作
        if int(count) > 200:
            raise serializers.ValidationError("超过上限!")
        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """对商品部分字段进行序列化"""
    count = serializers.IntegerField()
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields = ['id', 'count', 'name', 'default_image_url', 'price', 'selected']


# noinspection PyUnresolvedReferences,PyUnusedLocal
class CartDeleteSerializer(serializers.Serializer):
    """购物车数据删除序列化校验"""
    sku_id = serializers.IntegerField(min_value=1)


    def validate(self, attr):
        try:
            sku = SKU.objects.get(id=attr.get("sku_id"))
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品数据不存在!")

        return attr