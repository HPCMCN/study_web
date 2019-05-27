# coding = utf-8
import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_to_redis(request, user, response):
    """将cookie中的数据添加到redis中"""
    # 1. 获取cookie中的数据
    cookie_str = request.COOKIES.get("cart")
    if not cookie_str:
        return response
    cart_cookie = pickle.loads(base64.b64decode(cookie_str.encode()))
    # {sku_id: count}
    # 2. 获取redis中的数据
    cur = get_redis_connection("cart")
    cart_redis_str = cur.hgetall("cart_%s" % user.id)
    # 3. 将redis中二进制数据转化为整形
    cart = {int(sku_id): int(count) for sku_id, count in cart_redis_str.items()}
    # 4. 整理cookie数据到cart中, 如果存在就覆盖掉原有数据：
    selected_sku_id_list = []
    for sku_id, selected_count_dict in cart_cookie.items():
        cart[sku_id] = selected_count_dict["count"]
        # 5. 如果cookie中的sku_id被选中, 添加到选中列表中
        if selected_count_dict["selected"]:
            selected_sku_id_list.append(sku_id)
    # selected_sku_id_list = [sku_id
    #                         for sku_id, selected_count_dict in cart_cookie.items()
    #                         if selected_count_dict["selected"] and
    #                         not setattr(cart, "sku_id", selected_count_dict["count"])]
    # 6. 将整理后的数据合并得到购物车中
    if not all([cart, selected_sku_id_list]):
        # 如果没有选中的话, 就直接返回
        return response
    p1 = cur.pipeline()
    p1.hmset("cart_%s" % user.id, cart)
    # 注意拆包添加到redis中
    p1.sadd("cart_selected_%s" % user.id, *selected_sku_id_list)
    p1.execute()
    # 7. 清空cookie数据
    response.delete_cookie("cart")
    return response



