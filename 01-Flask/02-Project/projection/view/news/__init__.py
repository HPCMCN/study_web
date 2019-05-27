from flask import Blueprint

bp_new = Blueprint("bp_new", __name__, url_prefix="/news")


from . import new