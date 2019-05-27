# coding=utf-8
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from areas.views import AreasViewSet

router = DefaultRouter()
router.register(r"infos", AreasViewSet, base_name="area")

urlpatterns = [
    url(r'^',include(router.urls)),
    # url(r"^infos/(\d+)/", AreasViewSet.as_view)
]


# urlpatterns += router.urls
