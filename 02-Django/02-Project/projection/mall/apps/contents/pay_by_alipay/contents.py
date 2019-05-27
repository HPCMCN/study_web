# coding = utf-8

# app_id
import os

from mall.settings import BASE_DIR

ALIPAY_APP_ID = "2016091700530243"

# alipay网关url
ALIPAY_GATEWAY_URL = "https://openapi.alipaydev.com/gateway.do?"

# 私钥路径
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/app_keys/app_private_key.pem')

# alipay公钥
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/app_keys/app_public_key.pem')

# alipay是否开启debug模式
ALIPAY_DEBUG = True