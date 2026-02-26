import json

import requests
from authlib.common.security import generate_token
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
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

from app.auth import bp


def _oauth2_session() -> OAuth2Session:
    """
    Create and return an OAuth2Session configured for private_key_jwt.

    This session is configured to authenticate with the token endpoint
    using RFC 7523 private_key_jwt client authentication.
    """
    # Load the private signing key used for client authentication.
    # This is mounted via Docker secret and not stored in source control.
    with open(current_app.config["ONE_LOGIN_PRIVATE_KEY_PATH"], "rb") as f:
        private_key = f.read()

    return OAuth2Session(
        client_id=current_app.config["ONE_LOGIN_CLIENT_ID"],
        client_secret=private_key,
        scope="openid email phone",
        token_endpoint_auth_method=PrivateKeyJWT(f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/token"),
    )


def _verify_core_identity_jwt(core_identity_jwt: str) -> dict:
    """
    Verify and decode the coreIdentityJWT received from the userinfo endpoint.

    This function:
    1. Retrieves the DID document from the One Login internal host.
    2. Extracts assertionMethod public keys.
    3. Constructs a JWKS structure compatible with Authlib.
    4. Validates the JWT signature and standard claims.

    Args:
        core_identity_jwt: The signed JWT string returned in userinfo.

    Returns:
        The validated JWT claims as a dictionary.

    Raises:
        authlib.jose.errors.BadSignatureError:
            If signature validation fails.
        ValueError:
            If the JWKS is malformed or invalid.
    """
    # Fetch the DID document containing public keys used for signing.
    did = requests.get(f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/.well-known/did.json").json()

    keys = []

    # Extract each assertion method's public key and attach its key ID.
    for method in did.get("assertionMethod", []):
        jwk = method["publicKeyJwk"].copy()
        jwk["kid"] = method["id"]
        keys.append(jwk)

    # Build a JSON Web Key Set structure expected by Authlib.
    jwks = {"keys": keys}

    # Decode and validate the JWT signature and claims.
    claims = jwt.decode(core_identity_jwt, key=jwks)
    claims.validate()

    return claims


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
    client: OAuth2Session = _oauth2_session()

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
        return 400

    client: OAuth2Session = _oauth2_session()

    # Exchange authorization code for tokens.
    token = client.fetch_token(
        url=f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/token",
        redirect_uri=url_for("auth.callback", _external=True),
        code=request.args["code"],
        grant_type="authorization_code",
    )

    # Retrieve nonce for ID token validation.
    nonce: str | None = session.pop("oauth_nonce", None)

    # Fetch JWKS for ID token signature verification.
    jwks = requests.get(f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/.well-known/jwks.json").json()

    # Decode and validate ID token.
    claims = jwt.decode(
        token["id_token"],
        key=jwks,
        claims_cls=CodeIDToken,
        claims_options={"nonce": {"values": [nonce] if nonce else []}},
    )
    claims.validate()

    # Attach token to client for authenticated requests.
    client.token = token

    # Retrieve userinfo claims.
    userinfo = client.get(f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/userinfo").json()

    # Verify the core identity credential JWT.
    identity = _verify_core_identity_jwt(userinfo.get("https://vocab.account.gov.uk/v1/coreIdentityJWT"))

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
    userinfo: str | None = session.get("userinfo")

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
    id_token: str | None = session.pop("id_token", None)

    # Clear remaining session data.
    session.pop("userinfo", None)
    session.pop("identity", None)

    if id_token is None:
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
