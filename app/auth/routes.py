import json

import requests
from authlib.common.security import generate_token
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oidc.core import CodeIDToken
from flask import (
    Response,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import BadRequest

from app.auth import bp
from app.auth.utils import oauth2_session, verify_core_identity_jwt


@bp.route("/login")
def login() -> Response:
    """
    Initiate the OAuth 2.0 Authorization Code flow.

    This route:
    - Creates an OAuth session
    - Generates a nonce for ID token validation
    - Requests specific identity claims
    - Redirects the user to the One Login authorization endpoint
    """
    client: OAuth2Session = oauth2_session()

    # Nonce protects against replay attacks in ID token validation.
    nonce: str = generate_token()

    # Request specific additional claims from userinfo.
    claims: str = json.dumps(
        {
            "userinfo": {
                "https://vocab.account.gov.uk/v1/coreIdentityJWT": None,
                "https://vocab.account.gov.uk/v1/address": None,
            }
        }
    )

    # Vector of Trust requirement (P2 identity check).
    vtr: str = json.dumps(["Cl.Cm.P2"])

    uri, state = client.create_authorization_url(
        url=f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/authorize",
        redirect_uri=url_for("auth.callback", _external=True),
        nonce=nonce,
        claims=claims,
        vtr=vtr,
    )

    # Store state and nonce in session for CSRF and replay protection.
    session["oauth_state"] = state
    session["oauth_nonce"] = nonce

    return redirect(uri)


@bp.route("/callback")
def callback() -> Response:
    """
    Handle the OAuth callback from One Login.

    This route:
    - Validates the state parameter (CSRF protection)
    - Exchanges the authorization code for tokens
    - Validates the ID token (signature, nonce, claims)
    - Retrieves userinfo
    - Verifies the coreIdentityJWT
    - Stores session data
    """
    state: str | None = request.args.get("state")
    stored: str | None = session.pop("oauth_state", None)

    # Protect against CSRF attacks.
    if not stored or stored != state:
        raise BadRequest("Invalid OAuth state")

    client: OAuth2Session = oauth2_session()

    # Exchange authorization code for tokens.
    token: dict[str, object] = client.fetch_token(
        url=f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/token",
        redirect_uri=url_for("auth.callback", _external=True),
        code=request.args["code"],
        grant_type="authorization_code",
    )

    # Retrieve nonce for ID token validation.
    nonce: str | None = session.pop("oauth_nonce", None)

    # Fetch JWKS for ID token signature verification.
    jwks: dict[str, object] = requests.get(
        f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/.well-known/jwks.json"
    ).json()

    # Decode and validate ID token.
    claims = jwt.decode(
        str(token["id_token"]),
        key=jwks,
        claims_cls=CodeIDToken,
        claims_options={"nonce": {"values": [nonce] if nonce else []}},
    )
    claims.validate()

    # Attach token to client for authenticated requests.
    client.token = token  # type: ignore[assignment]

    # Retrieve userinfo claims.
    userinfo: dict[str, object] = client.get(f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/userinfo").json()

    # Verify the core identity credential JWT if present and a string.
    core_identity_jwt = userinfo.get("https://vocab.account.gov.uk/v1/coreIdentityJWT")
    identity: dict[str, object] | None = None
    if isinstance(core_identity_jwt, str):
        identity = verify_core_identity_jwt(core_identity_jwt)

    # Persist session information.
    session["id_token"] = token["id_token"]
    session["userinfo"] = userinfo
    session["identity"] = identity

    return redirect(url_for("auth.user"))


@bp.route("/user")
def user() -> str | Response:
    """
    Display authenticated user information.

    If no session data exists, the user is redirected to login.
    """
    userinfo = session.get("userinfo")
    if userinfo is None:
        return redirect(url_for("auth.login"))

    identity = session.get("identity")

    return render_template("user.html", userinfo=userinfo, identity=identity)


@bp.route("/logout")
def logout() -> Response:
    """
    Perform RP-initiated logout.

    This clears local session data and redirects to the One Login
    end-session endpoint with the required ID token hint.
    """
    id_token = session.pop("id_token", None)

    # Clear remaining session data.
    session.pop("userinfo", None)
    session.pop("identity", None)

    if not isinstance(id_token, str):
        return redirect(url_for("auth.logged_out"))

    end_session_url = f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/logout"
    post_logout = url_for("auth.logged_out", _external=True)

    # Construct logout URL according to OIDC RP-initiated logout spec.
    logout_url = f"{end_session_url}" f"?id_token_hint={id_token}" f"&post_logout_redirect_uri={post_logout}"

    return redirect(logout_url)


@bp.route("/logged-out")
def logged_out() -> str:
    """
    Render a simple logged-out confirmation page.
    """
    return render_template("logged-out.html")
