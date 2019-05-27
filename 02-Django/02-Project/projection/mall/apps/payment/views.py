from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from alipay import AliPay

from contents.pay_by_alipay.contents import *
from orders.models import OrderModel
from payment.models import Payment

alipay = AliPay(
            appid=ALIPAY_APP_ID,
            app_notify_url=None,
            app_private_key_path=APP_PRIVATE_KEY_PATH,
            alipay_public_key_path=ALIPAY_PUBLIC_KEY_PATH,
            sign_type='RSA2',
            debug=ALIPAY_DEBUG
        )


# noinspection PyUnresolvedReferences
class PaymentView(APIView):
    """支付宝支付"""
    # 1. 必须登陆
    # 2. 提供支付宝接口及对应参数
    # 3. 返回响应
    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderModel.objects.get(order_id=order_id,
                                      user=user,
                                      status=OrderModel.ORDER_STATUS_ENUM['UNPAID'])
        except OrderModel.DoesNotExist:
            return Response({"message": "订单数据有误!"})

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # 将浮点数转换为字符串
            subject='测试订单',
            return_url='http://www.meiduo.site:8080/pay_success.html',
        )
        alipay_url = ALIPAY_GATEWAY_URL + order_string
        return Response({"alipay_url": alipay_url})



class PaymentStatusView(APIView):
    """支付后的页面回调"""
    def put(self, request):
        data = request.query_params.dict()
        signature = data.pop("sign")
        if alipay.verify(data, signature):
            order_id = data.get("out_trade_no")
            trade_id = data.get("trade_no")
            Payment.objects.create(
                order_id = order_id,
                trade_id = trade_id
            )
            return Response({"trade_id": trade_id})
        return Response({"message": "支付失败!"}, status=status.HTTP_400_BAD_REQUEST)
