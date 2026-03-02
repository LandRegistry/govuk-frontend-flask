import json

import requests
from authlib.common.security import generate_token
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import JoseError, jwt
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
from werkzeug.exceptions import (
    BadGateway,
    BadRequest,
    InternalServerError,
    Unauthorized,
)

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
    try:
        client: OAuth2Session = oauth2_session()
    except Exception:
        current_app.logger.exception("Failed to create OAuth2 session")
        raise InternalServerError("Authentication unavailable.")

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

    try:
        uri, state = client.create_authorization_url(
            url=f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/authorize",
            redirect_uri=url_for("auth.callback", _external=True),
            nonce=nonce,
            claims=claims,
            vtr=vtr,
        )
    except KeyError:
        current_app.logger.exception("Missing configuration for One Login authorization endpoint")
        raise InternalServerError("Service misconfigured.")
    except Exception:
        current_app.logger.exception("Failed to create authorization URL")
        raise InternalServerError("Authentication unavailable.")

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
        current_app.logger.warning("Invalid OAuth state received. stored=%r incoming=%r", stored, state)
        raise BadRequest("Invalid OAuth state")

    try:
        client: OAuth2Session = oauth2_session()
    except Exception:
        current_app.logger.exception("Failed to create OAuth2 session in callback")
        raise InternalServerError("Authentication unavailable.")

    try:
        code = request.args["code"]
    except KeyError:
        current_app.logger.warning("Authorization code missing in callback")
        raise BadRequest("Missing authorization code")

    try:
        # Exchange authorization code for tokens.
        token: dict[str, object] = client.fetch_token(
            url=f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/token",
            redirect_uri=url_for("auth.callback", _external=True),
            code=code,
            grant_type="authorization_code",
        )
    except KeyError:
        current_app.logger.exception("Missing configuration for token endpoint")
        raise InternalServerError("Service misconfigured.")
    except requests.RequestException, TimeoutError:
        current_app.logger.exception("Network error while fetching token")
        raise BadGateway("Authentication temporarily unavailable.")
    except Exception:
        current_app.logger.exception("Unexpected error while fetching token")
        raise InternalServerError("Authentication failed.")

    # Retrieve nonce for ID token validation.
    nonce: str | None = session.pop("oauth_nonce", None)

    try:
        # Fetch JWKS for ID token signature verification.
        jwks_resp = requests.get(
            f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/.well-known/jwks.json",
            timeout=5,
        )
        jwks_resp.raise_for_status()
        jwks: dict[str, object] = jwks_resp.json()
    except KeyError:
        current_app.logger.exception("Missing configuration for JWKS endpoint")
        raise InternalServerError("Service misconfigured.")
    except requests.RequestException, TimeoutError, ValueError:
        current_app.logger.exception("Failed to retrieve or parse JWKS document")
        raise BadGateway("Authentication temporarily unavailable.")

    try:
        id_token_str = str(token["id_token"])
    except KeyError:
        current_app.logger.error("ID token missing from token response")
        raise BadGateway("Authentication failed.")

    try:
        # Decode and validate ID token.
        claims = jwt.decode(
            id_token_str,
            key=jwks,
            claims_cls=CodeIDToken,
            claims_options={"nonce": {"values": [nonce] if nonce else []}},
        )
        claims.validate()
    except JoseError:
        current_app.logger.exception("Failed to decode/validate ID token")
        raise Unauthorized("Authentication failed.")
    except Exception:
        current_app.logger.exception("Unexpected error validating ID token")
        raise InternalServerError("Authentication failed.")

    # Attach token to client for authenticated requests.
    client.token = token  # type: ignore[assignment]

    try:
        # Retrieve userinfo claims.
        userinfo_resp = client.get(f"{current_app.config["ONE_LOGIN_INTERNAL_HOST"]}/userinfo")
        userinfo_resp.raise_for_status()
        userinfo: dict[str, object] = userinfo_resp.json()
    except KeyError:
        current_app.logger.exception("Missing configuration for userinfo endpoint")
        raise InternalServerError("Service misconfigured.")
    except requests.RequestException, TimeoutError, ValueError:
        current_app.logger.exception("Failed to retrieve or parse userinfo")
        raise BadGateway("Authentication temporarily unavailable.")
    except Exception:
        current_app.logger.exception("Unexpected error fetching userinfo")
        raise InternalServerError("Authentication failed.")

    identity: dict[str, object] | None = None
    try:
        # Verify the core identity credential JWT if present and a string.
        core_identity_jwt = userinfo.get("https://vocab.account.gov.uk/v1/coreIdentityJWT")
        if isinstance(core_identity_jwt, str):
            identity = verify_core_identity_jwt(core_identity_jwt)
    except ValueError, JoseError:
        current_app.logger.exception("Failed to verify core identity JWT")
        identity = None
    except Exception:
        current_app.logger.exception("Unexpected error verifying core identity JWT")
        identity = None

    try:
        # Persist session information.
        session["id_token"] = id_token_str
        session["userinfo"] = userinfo
        session["identity"] = identity
    except Exception:
        current_app.logger.exception("Failed to persist session information")
        raise InternalServerError("Session error.")

    return redirect(url_for("auth.user"))


@bp.route("/user")
def user() -> str | Response:
    """
    Display authenticated user information.

    If no session data exists, the user is redirected to login.
    """
    userinfo = session.get("userinfo")
    if userinfo is None:
        current_app.logger.info("No user session found; redirecting to login")
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
    try:
        id_token = session.pop("id_token", None)
        # Clear remaining session data.
        session.pop("userinfo", None)
        session.pop("identity", None)
    except Exception:
        current_app.logger.exception("Failed to clear session during logout")
        return redirect(url_for("auth.logged_out"))

    if not isinstance(id_token, str):
        current_app.logger.info("No id_token found for RP-initiated logout; showing logged-out page")
        return redirect(url_for("auth.logged_out"))

    try:
        end_session_url = f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/logout"
        post_logout = url_for("auth.logged_out", _external=True)
        # Construct logout URL according to OIDC RP-initiated logout spec.
        logout_url = f"{end_session_url}" f"?id_token_hint={id_token}" f"&post_logout_redirect_uri={post_logout}"
    except KeyError:
        current_app.logger.exception("Missing configuration for logout endpoint")
        return redirect(url_for("auth.logged_out"))
    except Exception:
        current_app.logger.exception("Failed to construct logout URL")
        return redirect(url_for("auth.logged_out"))

    return redirect(logout_url)


@bp.route("/logged-out")
def logged_out() -> str:
    """
    Render a simple logged-out confirmation page.
    """
    return render_template("logged-out.html")
