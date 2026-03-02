import requests
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import current_app


def oauth2_session() -> OAuth2Session:
    """
    Create and return an OAuth2Session configured for private_key_jwt.

    This session is configured to authenticate with the token endpoint
    using RFC 7523 private_key_jwt client authentication.
    """
    # Load the private signing key used for client authentication.
    # This is mounted via Docker secret and not stored in source control.
    with open(current_app.config["ONE_LOGIN_PRIVATE_KEY_PATH"], "rb") as f:
        private_key: bytes = f.read()

    return OAuth2Session(
        client_id=str(current_app.config["ONE_LOGIN_CLIENT_ID"]),
        client_secret=private_key,
        scope="openid email phone",
        token_endpoint_auth_method=PrivateKeyJWT(f"{current_app.config["ONE_LOGIN_EXTERNAL_HOST"]}/token"),
    )


def verify_core_identity_jwt(core_identity_jwt: str) -> dict[str, object]:
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

    return dict(claims)
