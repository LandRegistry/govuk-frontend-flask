from flask import Blueprint

bp: Blueprint = Blueprint("auth", __name__, template_folder="../templates/auth")

from app.auth import routes  # noqa: E402,F401
