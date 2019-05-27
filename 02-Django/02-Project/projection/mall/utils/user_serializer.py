# coding=utf-8


def to_serializer(token, user):
    """用户登陆数据提供"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }