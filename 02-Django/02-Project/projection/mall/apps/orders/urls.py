# coding = utf-8
from django.conf.urls import url

from orders.views import OrderSettlementView, OrderCreateView

urlpatterns = [
    url(r'^places/$', OrderSettlementView.as_view(), name='placeorder'),
    url(r'^$', OrderCreateView.as_view(), name='commitorder'),
]
