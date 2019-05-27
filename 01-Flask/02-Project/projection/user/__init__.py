from flask import Blueprint

bp_user = Blueprint("bp_user", __name__, url_prefix="/user")
bp_admin = Blueprint("bp_admin", __name__, url_prefix="/admin")

from .user import *
from .admin import *


@bp_admin.before_request
@is_user_login
def check_permission():
    """权限校验"""
    print("检查权限")
    print(request.url)
    if not request.url.endswith("admin/login"):
        if not g.user:
            redirect("/")


@bp_admin.route("/logout")
def clear_session():
    """退出清理"""
    session.clear()
    return redirect("admin/login")