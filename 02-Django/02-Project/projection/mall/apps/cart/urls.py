# coding = utf-8

from django.conf.urls import url
from . import views

urlpatterns = [
    # /cart/
    url(r'^$', views.CartsView.as_view(), name='cart'),
]
