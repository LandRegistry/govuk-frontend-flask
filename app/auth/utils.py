import json

import requests
from authlib.integrations.requests_client import OAuth2Session
from authlib.jose import jwt
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import current_app


def oauth2_session() -> OAuth2Session:
    """
    Create and return an OAuth2Session configured for private_key_jwt.

    This session is used to authenticate with the token endpoint using the
    RFC 7523 private_key_jwt client authentication method. The private key is
    loaded from the path specified in ONE_LOGIN_PRIVATE_KEY_PATH.

    Configuration expected (from Flask's current_app.config):
        - ONE_LOGIN_CLIENT_ID: OAuth client ID (string)
        - ONE_LOGIN_PRIVATE_KEY_PATH: Filesystem path to the private key (string)
        - ONE_LOGIN_EXTERNAL_HOST: Base URL of the One Login external host (string)

    Logging:
        - Logs an error if the private key file cannot be read.
        - Logs an exception if constructing the OAuth2Session fails.

    Raises:
        FileNotFoundError: If the private key file cannot be found.
        OSError: If the private key file cannot be read.
        Exception: If the OAuth2Session cannot be constructed.
    """
    # Read the private signing key used for client authentication.
    # Typically mounted as a Docker/Kubernetes secret; never stored in source control.
    private_key_path = current_app.config["ONE_LOGIN_PRIVATE_KEY_PATH"]
    try:
        with open(private_key_path, "rb") as f:
            private_key: bytes = f.read()
    except FileNotFoundError:
        # Path is safe to log; do not log file contents.
        current_app.logger.error("Private key file not found at path: %s", private_key_path)
        raise
    except OSError as e:
        # Include strerror where available for clearer diagnostics.
        current_app.logger.error(
            "Failed to read private key from %s: %s",
            private_key_path,
            getattr(e, "strerror", str(e)),
        )
        raise

    # Build the OAuth2 session that signs client assertions with the loaded private key.
    external_host = current_app.config["ONE_LOGIN_EXTERNAL_HOST"]
    try:
        return OAuth2Session(
            client_id=str(current_app.config["ONE_LOGIN_CLIENT_ID"]),
            client_secret=private_key,  # Authlib accepts the raw private key bytes for PrivateKeyJWT
            scope="openid email phone",
            token_endpoint_auth_method=PrivateKeyJWT(f"{external_host}/token"),
        )
    except Exception:
        # Rare, but if session creation fails this gives context in logs while preserving the traceback.
        current_app.logger.exception("Error creating OAuth2Session for token endpoint %s/token", external_host)
        raise


def verify_core_identity_jwt(core_identity_jwt: str) -> dict[str, object]:
    """
    Verify and decode the coreIdentityJWT received from the userinfo endpoint.

    This function performs the following steps:
        1) Fetch the DID document from the internal host. The DID document
           contains public keys used by the issuer to sign the JWT.
        2) Extract the assertionMethod keys and construct a JWKS (JSON Web Key Set)
           structure that Authlib can use to verify the JWT signature.
        3) Decode and validate the JWT (signature and standard claims).

    Parameters:
        core_identity_jwt: The compact JWS (three-segment) string returned in the userinfo response.

    Returns:
        A plain dictionary of validated JWT claims.

    Configuration expected (from Flask's current_app.config):
        - ONE_LOGIN_INTERNAL_HOST: Base URL where the DID document is hosted (string)

    Logging:
        - Warns if the provided core_identity_jwt string is not in compact JWS format.
        - Logs errors for network timeouts, HTTP errors, and other request failures when fetching the DID.
        - Logs errors if the DID document is not valid JSON or has a malformed structure.
        - Logs an exception if JWT verification fails (the underlying Authlib exception is re-raised).

    Raises:
        ValueError:
            - If the provided core_identity_jwt is not a compact JWS.
            - If the DID document structure is missing required fields.
        requests.exceptions.RequestException:
            - For network or HTTP errors while downloading the DID document.
        authlib.jose.errors.BadSignatureError and other Authlib exceptions:
            - If JWT signature verification or claim validation fails.
    """
    # Quick sanity check: a compact JWS has exactly three segments separated by dots.
    # This prevents confusing errors further down if the input is clearly malformed.
    if not isinstance(core_identity_jwt, str) or core_identity_jwt.count(".") != 2:
        current_app.logger.warning("core_identity_jwt is not a compact JWS")
        raise ValueError("core_identity_jwt must be a compact JWS with three segments")

    # The DID document is published by the identity provider and lists the public keys
    # (assertionMethod) that can verify the JWT's signature.
    internal_host = current_app.config["ONE_LOGIN_INTERNAL_HOST"]
    did_url = f"{internal_host}/.well-known/did.json"

    # Fetch the DID document with a short timeout to avoid hanging requests.
    try:
        resp = requests.get(did_url, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        current_app.logger.error("Timeout retrieving DID document from %s", did_url)
        raise
    except requests.exceptions.HTTPError as e:
        # Include HTTP status where possible to aid troubleshooting.
        status = e.response.status_code if getattr(e, "response", None) is not None else "unknown"
        current_app.logger.error("HTTP %s retrieving DID document from %s", status, did_url)
        raise
    except requests.exceptions.RequestException as e:
        # Any other request-layer problem (connection errors, DNS, etc.).
        current_app.logger.error("Error retrieving DID document from %s: %s", did_url, str(e))
        raise

    # Parse the DID document JSON; log and re-raise if the payload is not valid JSON.
    try:
        did = resp.json()
    except json.JSONDecodeError:
        current_app.logger.error("DID document from %s is not valid JSON", did_url)
        raise

    # Extract each assertion method's public key (publicKeyJwk) and attach its key ID (id).
    # Authlib expects a JWKS structure like {"keys": [ {jwk+kid}, ... ] }.
    keys = []
    try:
        for method in did.get("assertionMethod", []):
            # Each method should be an object with "publicKeyJwk" and "id".
            jwk = method["publicKeyJwk"].copy()
            jwk["kid"] = method["id"]  # Attach the key ID so the verifier can select the right key.
            keys.append(jwk)
    except (KeyError, AttributeError, TypeError) as e:
        # If the DID document doesn't have the expected shape, surface a clear ValueError
        # and include a concise explanation in the log for operators.
        current_app.logger.error("Malformed DID document structure from %s: %s", did_url, str(e))
        raise ValueError("DID document is missing required fields for assertionMethod/publicKeyJwk/id") from e

    jwks = {"keys": keys}

    # Decode and validate the JWT using the keys from the DID document.
    # Authlib handles signature verification and standard claim validation (exp, nbf, iat) via validate().
    try:
        claims = jwt.decode(core_identity_jwt, key=jwks)
        claims.validate()
    except Exception:
        # Let specific Authlib exceptions bubble up; logging preserves context for diagnostics.
        current_app.logger.exception("JWT verification failed using keys from %s", did_url)
        raise

    # Convert Authlib's Claims object to a regular dict for callers.
    return dict(claims)
