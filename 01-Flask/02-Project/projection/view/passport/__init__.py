from flask import Blueprint

bp_validate = Blueprint("bp_validate", __name__, url_prefix="/passport")
from .passport import make_image