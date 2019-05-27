# coding=utf-8
from itsdangerous import TimedJSONWebSignatureSerializer as Ser
import itsdangerous
from mall.settings import SECRET_KEY

# 实例化加密对象, 设置密钥和有效期

ser_openid = Ser(SECRET_KEY, expires_in=3600)


def token_encode(data_to_encode):
    """加密openid"""

    # 加密, 返回值为二进制, 需要解码
    bytes_data = ser_openid.dumps(data_to_encode)
    data = bytes_data.decode()

    # 数据加密成token返回
    return data


def token_decode(data_to_decode):
    """解密openid
    :return 注意return dict
    """
    try:

        decode_data = ser_openid.loads(data_to_decode)

    except itsdangerous.BadData:
        return None

    return decode_data
