import time
from datetime import datetime, timedelta

from flask import render_template, request, redirect, session, url_for, g, jsonify

from user import bp_admin, datetime
from view.modules.models import User
from view.utils.common import is_user_login
from view.utils.response_code import RET


@bp_admin.route("/login", methods=["POST", "GET"])
def login():
    """后台管理登陆入口"""
    print("进入管理员登陆")
    if request.method == "GET":
        try:
            user_id = session["user_id"]
            is_admin = session["is_admin"]
            if is_admin:
                user = User.query.get(user_id)
            else:
                user = None
        except Exception:
            user = None
        if not user:
            return render_template("admin/login.html")
        return redirect(url_for("bp_admin.index"))
    elif request.method == "POST":
        password = request.form.get("password", None)
        name = request.form.get("username", None)
        try:
            user = User.query.filter(User.is_admin == True, User.nick_name == name).first()
        except Exception as error:
            print(error)
            return redirect("/")
        if not user:
            return redirect("/")
        if not user.check_password(password):
            return render_template("admin/login.html", errmsg="密码错误！")
        session["is_admin"] = True
        session["user_id"] = user.id
        return redirect("/admin/index")


@bp_admin.route("/index")
@is_user_login
def index():
    """后台主页面"""
    user = g.user_obj
    return render_template("admin/index.html", user=user)


@bp_admin.route("/count")
@is_user_login
def count():
    """后台统计人数"""
    try:
        now = time.localtime()
        mon_begin = "%d-%02d-01" % (now.tm_year, now.tm_mon)
        day_begin = "%d-%02d-%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        mon_end = datetime.strptime(mon_begin, "%Y-%m-%d")
        day_end = datetime.strptime(day_begin, "%Y-%m-%d")
        print(day_end)
    except Exception:
        return jsonify(errno=RET.IOERR, errmsg="时间获取失败")
    try:
        user_all = User.query.filter(User.is_admin == False).count()
        mon_count = User.query.filter(User.is_admin==False and mon_begin <= User.last_login < mon_end).count()
        day_count = User.query.filter(User.is_admin == False and day_begin <= User.last_login < day_end).count()
        now_time = datetime.strptime("{}{}{}".format(now.tm_year, now.tm_mon, now.tm_mday), "%Y%m%d")
        active_count = []
        active_time = []
        print("测试代码执行路径")
        for i in range(30):
            # print(i)
            active_begin = now_time - timedelta(days=i)
            active_end = now_time - timedelta(days=i - 1)
            # print("检测代码")
            active_day_count = User.query.filter(User.is_admin == False and active_begin <= User.last_login < active_end).count()
            active_count.append(int(active_day_count))
            active_time.append(active_begin.strftime('%Y-%m-%d'))
        active_count.reverse()
        active_time.reverse()
    except Exception as error:
        print("查询数据出错！", error)
        return jsonify(errno=RET.DATAERR, errmsg="数据获取失败")
    data = {
        "user_all": user_all,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }
    print(data)
    return render_template("admin/user_count.html", data=data)


@bp_admin.route("/list")
@is_user_login
def n_list():
    """后台列表形式统计"""
    user = g.user_obj
    return render_template("admin/user_list.html", user=user)


@bp_admin.route("/review")
@is_user_login
def review():
    """后台新闻审核"""
    user = g.user_obj
    return render_template("admin/news_review.html", user=user)


@bp_admin.route("/edit")
@is_user_login
def n_edit():
    """后台新闻编辑"""
    user = g.user_obj
    return render_template("admin/news_edit_detail.html", user=user)


@bp_admin.route("/type")
@is_user_login
def n_type():
    """后台新闻类型"""
    user = g.user_obj
    return render_template("admin/news_type.html", user=user)
