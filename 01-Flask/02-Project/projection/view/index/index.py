from flask import render_template, current_app, jsonify, request

from view.utils.common import *
from view.utils.response_code import RET
from ..index import bp_index


def search_category():
    """获取新闻种类"""
    # 获取所有新闻种类
    categorys_obj = Category.query.all()
    # 把对象转化成列表套字典形式
    category_list = objs_to_list_dict(categorys_obj)
    return category_list


@bp_index.route("/")
@is_user_login
def index():
    """主页"""
    # 校验用户是否登陆
    user = g.user
    # 获取点击排行榜
    click_news_list = search_new()
    # 获取分类数据
    category_list = search_category()
    # print("user为： ", user)
    data = {
        "user_info": user,
        "click_news_list": click_news_list,
        "category_list": category_list
    }
    # print("查询完毕data为：")
    # print(data)

    return render_template("news/index.html", data=data if data else None)


@bp_index.route("/favicon.ico")
def ico():
    """ico"""
    return current_app.send_static_file("news/favicon.ico")


@bp_index.route("/news_list")
def index_news_list():
    """获取各种类型的新闻列表"""
    # 获取种类id， 页数page， 当前加载的总数per_page
    cid = request.args.get("cid")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", constants.HOME_PAGE_MAX_NEWS))
    errno, errmsg = RET.OK, "OK"
    news_list, pages = None, []
    try:
        print("获取新闻列表", cid, page, per_page)
        # 利用cid查询相应的类别， 当是默认的1时表示当前查询所有新闻并以时间倒序形式展现出来
        pageinate = News.query.filter(*([] if cid == "1"
                                        else [News.category_id == cid])).order_by(News.create_time.desc())
        pageinate = pageinate.paginate(page, per_page, False)
        # 获取当前的起始页数和当前总数 flask内置方法
        page = pageinate.page
        pages = pageinate.pages
        # 将对象转化成列表套字典形式
        news_list = objs_to_list_dict(pageinate.items)
    except Exception as error:
        print(error)
        errno, errmsg = RET.DATAERR, "获取数据出错"
    print(news_list)
    data = {
        "errno": errno,
        "errmsg": errmsg,
        "total_page": pages,
        "current_page": page,
        "news_dict_li": news_list
    }

    return jsonify(data)