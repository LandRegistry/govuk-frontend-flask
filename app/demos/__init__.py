from flask import Blueprint

bp = Blueprint("demos", __name__, template_folder="../templates/demos")

from app.demos import routes  # noqa: E402,F401
