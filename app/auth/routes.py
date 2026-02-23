import requests
from authlib.common.security import generate_token
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from authlib.oidc.core import CodeIDToken
from flask import current_app, redirect, render_template, request, session, url_for

from app.auth import bp


def _oauth2_session() -> OAuth2Session:
    """Create an OAuth2Session configured for private_key_jwt."""

    # Read the private key
    with open(current_app.config["ONE_LOGIN_PRIVATE_KEY_PATH"], "rb") as f:
        private_key = f.read()

    session = OAuth2Session(
        client_id=current_app.config["ONE_LOGIN_CLIENT_ID"],
        client_secret=private_key,
        scope="openid email phone",
        token_endpoint_auth_method=PrivateKeyJWT(current_app.config["ONE_LOGIN_PUBLIC_TOKEN_URL"]),
    )

    return session


@bp.route("/login")
def login():
    client = _oauth2_session()
    nonce = generate_token()
    uri, state = client.create_authorization_url(
        url=current_app.config["ONE_LOGIN_AUTHORIZE_URL"],
        redirect_uri=url_for("auth.callback", _external=True),
        nonce=nonce,
    )
    session["oauth_state"] = state
    session["oauth_nonce"] = nonce
    return redirect(uri)


@bp.route("/callback")
def callback():
    state = request.args.get("state")
    stored = session.pop("oauth_state", None)
    if not stored or stored != state:
        return 400

    client = _oauth2_session()

    token = client.fetch_token(
        url=current_app.config["ONE_LOGIN_ACCESS_TOKEN_URL"],
        redirect_uri=url_for("auth.callback", _external=True),
        code=request.args["code"],
        grant_type="authorization_code",
    )

    nonce = session.pop("oauth_nonce", None)
    keys = requests.get(current_app.config["ONE_LOGIN_JWKS_URL"]).json()

    claims = jwt.decode(
        token["id_token"],
        keys,
        claims_cls=CodeIDToken,
        claims_options={"nonce": {"values": [nonce]}},
    )
    claims.validate()

    client.token = token
    userinfo = client.get(current_app.config["ONE_LOGIN_USERINFO_URL"]).json()

    session["id_token"] = token["id_token"]
    session["userinfo"] = userinfo

    return redirect(url_for("main.index"))


@bp.route("/logout")
def logout():
    pass


@bp.route("/logged-out")
def logged_out() -> str:
    return render_template("logged-out.html")
