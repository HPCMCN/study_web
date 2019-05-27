import functools

from flask import session, g, current_app

from view.modules.models import *


def built_floor(new_id):
    """盖楼"""
    print(new_id)
    parent = None
    son_parent_list = []

    try:
        comment_parent_obj = Comment.query.filter(Comment.news_id == new_id and Comment.parent_id is None).all()
        print("这是parent: ",comment_parent_obj)
        comment_son_obj = Comment.query.filter(Comment.parent_id is not False).all()
        print("这是son: ", comment_son_obj)
        for comment_parent in comment_parent_obj if comment_parent_obj else "":
            son_list = []
            for comment_son in comment_son_obj if comment_son_obj else "":
                # 当评论父id和当前id相等时， 说明存在父子关系
                try:
                    # print(comment_son.parent_id, comment_parent.id)
                    if comment_son.parent.id == comment_parent.id:
                        # 将对象转化成字典
                        parent = comment_parent.to_dict()
                        son = comment_son.to_dict()
                        son_list.append(son)
                except Exception as error:
                    current_app.logger.error(error)

            # son为空说明没有子类
            if len(son_list) == 0:
                # 如果没有子类就把子类赋值空列表
                user, user_obj = get_session()
                comment_like_count = False
                if user:
                    comment_like_count = CommentLike.query.filter(CommentLike.comment_id == comment_parent.id,
                                                                  CommentLike.user_id == user_obj.id).count()
                parent = comment_parent.to_dict()
                parent["is_like"] = True if comment_like_count else False
                son_parent_list.append({"parent": parent, "son": []})
            else:
                # 以列表套字典的形式传递
                # print(son_list)
                son_parent_list.append({"parent": parent, "son": son_list})
        print(son_parent_list)
    except Exception as error:
        print(error)
    return son_parent_list if son_parent_list else []


def filter_hot(index):
    """热度过滤器"""
    return "first" if index == 0 else "second" if index == 1 else "third" if index == 2 else ""


def get_session():
    """获取session查询, 实现免登陆"""
    user_id = session.get("user_id")
    # print("已进入查询： ", user_id)
    user = None
    user_obj = None
    try:
        user_obj = User.query.get(user_id)
        user = user_obj.to_dict()
    except Exception:
        print("数据库不存在！")
    # print("查询成功： ", user_id)
    return user, user_obj


def is_user_login(view_func):
    @functools.wraps(view_func)
    def wrap(*args, **kwargs):
        g.user, g.user_obj = get_session()
        return view_func(*args, **kwargs)

    return wrap


def objs_to_list_dict(objs):
    """把每个对象都遍历出来, 改为字典"""
    list_dict = []
    for obj in objs if objs else "":
        list_dict.append(obj.to_dict())
    return list_dict


def search_new():
    """到数据库查询数据并返回数据"""
    # 获取所有数据, 现在得到的是所有new的对象
    news_obj = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    # 将对象转化成字典形式， 并封装到列表中
    news_list = objs_to_list_dict(news_obj)
    return news_list
