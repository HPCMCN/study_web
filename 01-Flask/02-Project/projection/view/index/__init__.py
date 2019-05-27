from flask import Blueprint

bp_index = Blueprint("bp_index", __name__)

from .index import index