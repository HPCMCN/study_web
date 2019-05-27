# coding=utf-8

import os
from mall.settings import BASE_DIR

# fastdfs客户端的配置路径
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, "app_keys/fastdfs/client.conf")

# fastdfs的ip端口
FDFS_URL = "http://10.254.1.55:8888/"


GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(BASE_DIR), "front")



