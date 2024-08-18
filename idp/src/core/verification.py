import json
from datetime import UTC, datetime

from jwcrypto.jwt import JWS, JWT, JWKSet
from services.oidc_client import OIDCClient


async def verify_token(oidc_client: OIDCClient, access_token: str) -> dict:
    """
    Verifies access token and returns claims if verification passed
    """

    # check if token has signature and was decoded
    jws = JWT(jwt=access_token).token
    if not isinstance(jws, JWS):
        raise ValueError("Signed token expected")

    # verify signature
    if not isinstance(jws.jose_header, dict):
        raise ValueError("Failed to decode signing info")

    jwks = await oidc_client.jwks_raw()
    set = JWKSet.from_json(json.dumps(jwks))
    jws.verify(set)
    if not jws.verifylog or jws.verifylog[0] != "Success":
        raise ValueError("Signiture failed")

    if not jws.payload:
        raise ValueError("Token payload is not verified")

    payload = json.loads(jws.payload)

    # verify issuer
    issuer = await oidc_client.issuer()
    if payload["iss"] != issuer:
        raise ValueError("Wrong issuer")

    # verify expiration
    now = datetime.now(UTC).timestamp()
    exp = payload["exp"]
    if not exp:
        raise ValueError("Expiration not set")

    # `iat` (token issued time) can be used with
    # security incidents, it must be older than last incident

    if exp < now:
        raise ValueError("Token has expired")

    # This verification is optional and not part of OAuth
    if payload["azp"] != oidc_client.client_id:
        raise ValueError("Wrong client id")

    return dict(payload)
