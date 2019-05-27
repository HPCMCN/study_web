# coding=utf-8

# GET /verifications/smscodes/(?P<mobile>1[345789]\d{9})/?text=xxxx & image_code_id=xxxx
# GET /verifications/imagecodes/(?P<image_code_id>.+)/
from django.conf.urls import url

from verifications import views

urlpatterns = [
    url(r"^smscodes/(?P<mobile>1[345789]\d{9})/$", views.RegisterSMSCodeView.as_view(), name="sms_code"),
    url(r"^imagecodes/(?P<image_code_id>.+)/$", views.ImageCodeAPIView.as_view(), name="image_code"),
]
