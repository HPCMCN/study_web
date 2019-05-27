import datetime

from flask import render_template, url_for, current_app, redirect, request, session, jsonify

from user import bp_user
from view.index.index import search_category, search_new, g, objs_to_list_dict
from view.modules.models import *
from view.utils.common import is_user_login
from view.utils.image_storge import storage
from view.utils.response_code import RET


@bp_user.route("/info")
@is_user_login
def info():
    # 校验用户是否登陆
    user = g.user
    if not user:
        print(current_app.url_map)
        return redirect(url_for("bp_index.index"))
    # 获取点击排行榜
    click_news_list = search_new()
    # 获取分类数据
    category_list = search_category()
    # print("user为： ", user)
    g.user_obj.last_login = datetime.now()
    db.session.commit()
    data = {
        "user_info": user,
        "click_news_list": click_news_list,
        "category_list": category_list
    }
    return render_template("news/user.html", data=data)


@bp_user.route("/pic/info", methods=["POST", "GET"])
@is_user_login
def pic_info():
    """头像设置"""
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user
        }
        return render_template("news/user_pic_info.html", data=data)
    elif request.method == "POST":
        avatar = request.files.get("avatar").read()
        if not avatar:
            return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
        url = storage(avatar)
        g.user_obj.avatar_url = url
        db.session.commit()
        return jsonify(errno=RET.OK, errmsg="OK")


@bp_user.route("/follow")
@is_user_login
def follow():
    """我的关注"""
    user = g.user_obj
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="请登录！")
    print(user.followers.paginate(1, 3, error_out=False).items)
    data = {}

    return render_template("news/user_follow.html", data=data)


@bp_user.route("/news/release", methods=["POST", "GET"])
@is_user_login
def news_release():
    """新闻发布"""
    if request.method == "GET":
        categorys_obj = Category.query.all()
        category_list = objs_to_list_dict(categorys_obj)
        category_list.pop(0)
        data = {"categorys": category_list}
        print(data)
        return render_template("news/user_news_release.html", data=data)
    elif request.method == "POST":
        data = request.form
        print(data)
        title = data.get("title")
        try:
            index_image = request.files.get("index_image").read()
        except Exception as error:
            print(error)
            index_image = None
        content = data.get("content")
        category_id = data.get("category_id")
        digest = data.get("digest")
        if not all([title, index_image, content, category_id, digest]):
            return jsonify(errno=RET.NODATA, errmsg="数据不能为空！")
        try:
            key = storage(index_image)
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(error=RET.THIRDERR, errmsg="三方出错！")
        new = News()
        new.title = title
        new.category_id = category_id
        new.digest = digest
        new.content = content
        new.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        new.source = "个人发布"
        new.user_id = g.user_obj.id
        new.status = 1
        try:
            db.session.add(new)
            db.session.commit()
        except Exception as error:
            current_app.logger.error(error)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="存储数据库失败！")
        return jsonify(errno=RET.OK, errmsg="OK")


@bp_user.route("/pass/info", methods=["POST", "GET"])
@is_user_login
def pass_info():
    """修改密码"""
    if request.method == "GET":
        return render_template("news/user_pass_info.html", data={"user_info": g.user})
    elif request.method == "POST":
        print(request.json)
        old_password = request.json.get("old_password")
        new_password = request.json.get("new_password")
        new_password2 = request.json.get("new_password2")
        if not all([old_password, new_password, new_password2]):
            return jsonify(errno=RET.PARAMERR, errmsg="密码不能为空！")
        if new_password != new_password2:
            return jsonify(errno=RET.PWDERR, errmsg="密码输入不一致！")
        if not g.user_obj.check_password(old_password):
            return jsonify(errno=RET.PWDERR, errmsg="原密码输入错误！")
        g.user_obj.password = new_password
        try:
            db.session.commit()
        except Exception as error:
            print(error)
            return jsonify(errno=RET.DBERR, errmsg="密码提交出错！")
        return jsonify(errno=RET.OK, errmsg="OK")


@bp_user.route("/collection")
@is_user_login
def collection():
    """我的收藏"""
    p = int(request.args.get("p", 1))
    collections = g.user_obj.collection_news.paginate(p, 2, False)
    collection_list = objs_to_list_dict(collections.items)
    page = collections.page
    pages = collections.pages

    print(collection_list, pages, page)
    data = {
        "collections": collection_list,
        "current_page": page,
        "total_page": pages
    }
    return render_template("news/user_collection.html", data=data)


@bp_user.route("/news/list")
@is_user_login
def news_list():
    """新闻列表"""
    user = g.user_obj
    new_list = objs_to_list_dict(user.news_list.all())
    print(new_list, )
    return render_template("news/user_news_list.html", data={"news_list": new_list})


@bp_user.route("/base/info", methods=["POST", "GET"])
@is_user_login
def base_info():
    """基本信息"""
    print("处理基本信息！")
    user = g.user_obj
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user_info": user.to_dict()})
    elif request.method == "POST":
        gender = request.json.get("gender")
        nick_name = request.json.get("nick_name")
        signature = request.json.get("signature")

        if all([gender, nick_name, signature]):
            print(gender, nick_name, signature)
            user.gender = gender
            user.nick_name = nick_name
            user.signature = signature
            try:
                db.session.commit()
            except Exception as error:
                print(error)
        print("数据更新成功！")
        print(user.to_dict())
        session["nick_name"] = nick_name
        return jsonify(errno=RET.OK, errmsg="OK")
