from flask import Blueprint

bp = Blueprint("links", __name__)

from app.links import routes