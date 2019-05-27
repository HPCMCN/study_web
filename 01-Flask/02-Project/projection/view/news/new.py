from flask import render_template, request, jsonify, current_app

from view.news import bp_new
from view.utils.common import *
from view.utils.response_code import RET


@bp_new.route("/<int:new_id>")
@is_user_login
def detail(new_id):
    # 校验用户是否登陆
    user = g.user
    print(user)
    # 获取点击排行榜
    click_news_list = search_new()
    new_obj = News.query.get(new_id)
    new = new_obj.to_dict()
    is_collection, collections = None, None
    son_parent_list = built_floor(new_id)  # 盖楼
    length = len(son_parent_list)
    if user:
        is_collection = True if News.query.get(new_id) in g.user_obj.collection_news.all() else False
    data = {
        "user_info": user,
        "click_news_list": click_news_list,
        "new": new,
        "is_collection": is_collection,
        "son_parent_list": son_parent_list,
        "length": length
    }
    try:
        return jsonify(errno=RET.OK, errmsg="OK")
    finally:
        return render_template("news/detail.html", data=data)


@bp_new.route("/news_collect", methods=["POST"])
@is_user_login
def news_collect():
    """收藏处理"""
    new_id = request.json.get("new_id")
    action = request.json.get("action")
    print(new_id, action)
    if not g.user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登陆！")
    if not all([new_id, True if action in ["collect", "cancel_collect"] else None]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能有空！")
    try:
        news_obj = News.query.get(new_id)
        print(news_obj)
    except Exception as error:
        return jsonify(errno=RET.DATAERR, errmsg=error)
    if not news_obj:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在！")
    if action == "collect":
        print("收藏！", g.user_obj)
        if news_obj not in g.user_obj.collection_news.all():
            g.user_obj.collection_news.append(news_obj)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="已收藏！")

    elif action == "cancel_collect":
        print("取消收藏！")
        g.user_obj.collection_news.remove(news_obj)

    try:
        db.session.commit()
    except Exception as error:
        current_app.logger.error(error)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据提交失败！")

    return jsonify(errno=RET.OK, errmsg="收藏成功")


@bp_new.route("/news_comment", methods=["POST"])
@is_user_login
def news_comment():
    """回复评论"""
    print(request.json)
    if not g.user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登录！")
    comment_str = request.json.get("comment")
    new_id = request.json.get("new_id")
    parent_id = request.json.get("parent_id")
    if not all([comment_str, new_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="提交数据不能为空！")
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="请登录！")
    try:
        new_obj = News.query.get(new_id)
    except Exception as error:
        print(error)
        return jsonify(errno=RET.DBERR, errmsg="ID查询不到！")
    if not new_obj:
        return jsonify(errno=RET.NODATA, errmsg="相关新闻已删除！")
    comment = Comment()
    comment.user_id = g.user_obj.id
    comment.news_id = new_id
    comment.parent_id = parent_id
    comment.content = comment_str
    print(comment.content)
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as error:
        print(error)
        return jsonify(errno=RET.DBERR, errmsg="数据提交失败！")
    print("数据提交成功！")
    return jsonify(errno=RET.OK, errmsg="数据提交成功！")


@bp_new.route("/comment_like", methods=["POST"])
@is_user_login
def comment_like():
    print(request.json)
    user = g.user_obj
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登陆！")
    action = request.json.get("action")
    comment_id = request.json.get("comment_id")
    new_id = request.json.get("news_id")
    if not all([action, comment_id, new_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="前端参数传递为空！")
    try:
        comment = Comment.query.get(comment_id)
        comment_like = CommentLike.query.filter(CommentLike.user_id == user.id and CommentLike.comment_id == comment_id).first()
        print(comment_like)
        if comment and action == "add" and not comment_like:
            comment_obj = CommentLike()
            comment_obj.comment_id = comment_id
            comment_obj.user_id = user.id
            comment.like_count += 1
            db.session.add(comment_obj)
            db.session.commit()
        elif comment and comment_like:
            print()
            db.session.delete(comment_like)
            comment.like_count -= 1
            db.session.commit()
        else:
            return jsonify(errno=RET.PARAMERR, errmsg="参数传递错误！")
        db.session.commit()
        print("点赞系统成功执行")
    except Exception as error:
        current_app.logger.error(error)
    return jsonify(errno=RET.OK, errmsg="OK")

@bp_new.route("followed_user")
@is_user_login
def followed_user():
    """关注作者"""
    user = g.user_obj
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登陆！")
    print(request.json)
    return jsonify(errno=RET.OK, errmsg="OK")
