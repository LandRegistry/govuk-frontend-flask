from flask import redirect, render_template, session, url_for

from app import oauth
from app.auth import bp


@bp.route("/login")
def login():
    redirect_uri = url_for("auth.authorize", _external=True)
    return oauth.one_login.authorize_redirect(redirect_uri)


@bp.route("/authorize")
def authorize():
    token = oauth.one_login.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect(url_for("main.index"))


@bp.route("/logout")
def logout():
    id_token = session.pop("user", None)
    return oauth.one_login.logout_redirect(
        post_logout_redirect_uri=url_for("auth.logged_out", _external=True),
        id_token_hint=id_token,
    )


@bp.route("/logged-out")
def logged_out():
    state_data = oauth.one_login.validate_logout_response()
    return render_template("logged-out.html", state_data=state_data)
