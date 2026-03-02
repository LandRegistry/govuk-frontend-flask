import json

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
    private_key_path = current_app.config["ONE_LOGIN_PRIVATE_KEY_PATH"]
    try:
        with open(private_key_path, "rb") as f:
            private_key: bytes = f.read()
    except FileNotFoundError:
        current_app.logger.error("Private key file not found at path: %s", private_key_path)
        raise
    except OSError as e:
        current_app.logger.error(
            "Failed to read private key from %s: %s",
            private_key_path,
            getattr(e, "strerror", str(e)),
        )
        raise

    external_host = current_app.config["ONE_LOGIN_EXTERNAL_HOST"]
    try:
        return OAuth2Session(
            client_id=str(current_app.config["ONE_LOGIN_CLIENT_ID"]),
            client_secret=private_key,
            scope="openid email phone",
            token_endpoint_auth_method=PrivateKeyJWT(f"{external_host}/token"),
        )
    except Exception:
        # Rare, but gives context if the client construction fails
        current_app.logger.exception("Error creating OAuth2Session for token endpoint %s/token", external_host)
        raise


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
    # Minimal sanity check; keeps errors clearer earlier
    if not isinstance(core_identity_jwt, str) or core_identity_jwt.count(".") != 2:
        current_app.logger.warning("core_identity_jwt is not a compact JWS")
        raise ValueError("core_identity_jwt must be a compact JWS with three segments")

    internal_host = current_app.config["ONE_LOGIN_INTERNAL_HOST"]
    did_url = f"{internal_host}/.well-known/did.json"

    # Fetch the DID document containing public keys used for signing.
    try:
        resp = requests.get(did_url, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        current_app.logger.error("Timeout retrieving DID document from %s", did_url)
        raise
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if getattr(e, "response", None) is not None else "unknown"
        current_app.logger.error("HTTP %s retrieving DID document from %s", status, did_url)
        raise
    except requests.exceptions.RequestException as e:
        current_app.logger.error("Error retrieving DID document from %s: %s", did_url, str(e))
        raise

    try:
        did = resp.json()
    except json.JSONDecodeError:
        current_app.logger.error("DID document from %s is not valid JSON", did_url)
        raise

    keys = []
    try:
        # Extract each assertion method's public key and attach its key ID.
        for method in did.get("assertionMethod", []):
            jwk = method["publicKeyJwk"].copy()
            jwk["kid"] = method["id"]
            keys.append(jwk)
    except (KeyError, AttributeError, TypeError) as e:
        # Re-raise to surface as ValueError but log the problem
        current_app.logger.error("Malformed DID document structure from %s: %s", did_url, str(e))
        raise ValueError("DID document is missing required fields for assertionMethod/publicKeyJwk/id") from e

    jwks = {"keys": keys}

    try:
        claims = jwt.decode(core_identity_jwt, key=jwks)
        claims.validate()
    except Exception:
        # Let Authlib exceptions propagate, but log for diagnostics
        current_app.logger.exception("JWT verification failed using keys from %s", did_url)
        raise

    return dict(claims)
