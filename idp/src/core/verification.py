import json
from datetime import UTC, datetime

from jwcrypto.jwt import JWS, JWT, JWKSet
from services.keycloak_client import KeycloackClient


async def verify_token(client: KeycloackClient, access_token: str, strict: bool = False) -> dict:
    """
    Verifies access token and returns claims in verification passed
    """
    # TODO: Use OIDC client, we don't need keycloak here

    if strict:
        # TODO: Check if it works
        if not await client.user_token_introspect(access_token):
            raise ValueError("Verification failed")

    jws = JWT(jwt=access_token).token

    jwks = await client.oidc_jwks_raw()

    # check if token has signature and was decoded
    if not isinstance(jws, JWS):
        raise ValueError("Signed token expected")

    if isinstance(jws.jose_header, dict):
        # verify signature
        set = JWKSet.from_json(json.dumps(jwks))
        jws.verify(set)
        if not jws.verifylog or jws.verifylog[0] != "Success":
            raise ValueError("Signiture failed")
    else:
        raise ValueError("Failed to decode signing info")

    if not jws.payload:
        raise ValueError("Token payload is not verified")

    payload = json.loads(jws.payload)

    # verify issuer
    issuer = await client.oidc_issuer()
    if payload["iss"] != issuer:
        raise ValueError("Wrong issuer")

    # verify expiration
    now = datetime.now(UTC).timestamp()
    exp = payload["exp"]
    if not exp:
        raise ValueError("Expiration not set")

    if exp < now:
        raise ValueError("Token has expired")

    # This verification is optional and not part of OAuth
    if payload["azp"] != client.client_id:
        raise ValueError("Wrong client id")

    return payload
