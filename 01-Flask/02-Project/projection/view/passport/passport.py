from datetime import datetime
import random
import re

from flask import request, make_response, jsonify, session, url_for

from view import redis_store, db
from view.constants import *
from view.modules.models import User
from view.passport import bp_validate
from view.utils.captcha.captcha import captcha
from view.utils.response_code import RET
from view.utils.yuntongxun.sms import CCP


@bp_validate.route("/image_code/")
def make_image():
    """图片验证制作"""
    # 获取UUID随机唯一字符
    print("进入图片验证制作")
    code_id = request.args.get("code_id")
    answer, image = captcha.generate_captcha()
    print(answer)
    image_key = "image_code_" + code_id
    # print(name, answer, redis_store)
    # 添加到redis中 k_v_lift'time
    try:
        # 防止redis未打开
        redis_store.set(image_key, answer, IMAGE_CODE_REDIS_EXPIRES)
    except Exception as error:
        return jsonify(errno=RET.DATAERR, errmsg=error)
    # 二进制数据不能直接return
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response


@bp_validate.route("/sms_code", methods=["POST"])
def make_sms():
    """短信验证码制作"""
    print("进入短信注册")
    dict_code = request.json
    print(dict_code)
    mobile = dict_code.get("mobile")
    image_code = dict_code.get("image_code")
    code_id = dict_code.get("code_id")
    # 非空判断
    if not all([mobile, image_code, code_id]):
        redis_store.delete("image_code_" + code_id)
        return jsonify(errno=RET.NODATA, errmsg="不能有空数据")
    # 手机号校验
    if not re.match(r"^1[35678]\d{9}$", mobile):
        redis_store.delete("image_code_" + code_id)
        return jsonify(errno=RET.DATAERR, errmsg="手机号输入有误, 请重试！")
    try:
        # 防止数据过期报错
        answer = redis_store.get("image_code_" + code_id)
    except Exception:
        redis_store.delete("image_code_" + code_id)
        return jsonify(errno=RET.DBERR, errmsg="图片已过期, 请刷新图片！")
    if image_code.upper() != answer.upper():
        redis_store.delete("image_code_" + code_id)
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误！")

    random_code = "%{}d".format(len(str(MOBILE_VALIDATE_MAX))) % random.randint(MOBILE_VALIDATE_MIN, MOBILE_VALIDATE_MAX)
    print(random_code)
    redis_store.set("sms_code_" + mobile, random_code, IMAGE_CODE_REDIS_EXPIRES)
    result = CCP().send_template_sms(mobile, [random_code, MOBILE_VALIDATE_EXPIRES], MOBILE_TEMPLATE)
    print("校验成功！")
    return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败, 请稍后重试！") if result else jsonify(errno=RET.OK,
                                                                                          errmsg="ok")


@bp_validate.route("/register", methods=["POST"])
def validate_register():
    print("正在进行登陆校验")
    form_code = request.json
    print(form_code)
    sms_code = form_code.get("sms_code")
    mobile = form_code.get("mobile")
    password = form_code.get("password")
    if not all([sms_code, mobile, password]):
        try:
            redis_store.delete("sms_code_" + mobile)
        except Exception:
            print("删除无用记录出错code_1")
        return jsonify(errno=RET.NODATA, errmsg="输入信息中不能有空！")
    try:
        sms_code_mobile = redis_store.get("sms_code_" + mobile)
    except Exception:
        print("删除无用记录出错code_2")
        redis_store.delete("sms_code_" + mobile)
        return jsonify(error=RET.DBERR, errmsg="验证码已过期！")
    if sms_code != sms_code_mobile:
        print("删除无用记录出错code_3")
        print(sms_code, sms_code_mobile)
        redis_store.delete("sms_code_" + mobile)
        return jsonify(errno=RET.DATAERR, errmsg="手机验证码输入错误！")
    print("通过校验！")
    user = User()
    print(user)
    user.nick_name = mobile
    print(password)
    user.password = password
    user.last_login = datetime.now()
    user.mobile = mobile
    db.session.add(user)
    db.session.commit()
    print("用户已成功注册！")
    return jsonify(errno=RET.OK, errmsg="ok")


@bp_validate.route("/login", methods=["POST"])
def login():
    """登陆处理"""
    print("用户正在进行登陆操作")
    login_code = request.json
    print(login_code)
    mobile = login_code.get("mobile")
    validate_password = login_code.get("password")
    if not all([mobile, validate_password]):
        return jsonify(errno=RET.NODATA, errmsg="账号密码不能为空！")
    try:
        user = User.query.filter(User.mobile == mobile).all()[0]
    except Exception:
        return jsonify(errno=RET.ROLEERR, errmsg="用户名不存在！")
    if not user.check_password(validate_password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误!")
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["user_id"] = user.id
    user.last_login = datetime.now()
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="ok")


@bp_validate.route('/logout')
def logout():
    session.pop("mobile")
    session.pop("nick_name")
    session.pop("user_id")
    return jsonify(errno=RET.OK, errmsg="OK")

