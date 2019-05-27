# coding=utf-8


import os

from django.conf.urls import url, include
# from django.contrib import admin

import xadmin
from mall.settings import BASE_DIR


def auto_append_url(input_url="app"):
    """路由的正则和命名空间以文件夹名命名"""
    base_url = BASE_DIR[:] + "/" + input_url
    urlpatterns = [
        # url(r'^admin/', admin.site.urls),
        url(r'^ckeditor/', include('ckeditor_uploader.urls')),
        url(r'xadmin/', include(xadmin.site.urls)),
    ]
    list_file = os.listdir(path=base_url)
    for file in list_file:
        a = base_url + "/" + file
        if os.path.isdir(a) and file != os.path.basename(base_url):
            if "urls.py" in os.listdir(path=a):
                urlpatterns.append(
                    url(r"^" + file + "/", include(file + ".urls", namespace=file)),
                )
    return urlpatterns
