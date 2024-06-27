from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class JWKSKey(BaseModel):
    """
    Described https://datatracker.ietf.org/doc/html/rfc7517
    """

    model_config = ConfigDict(strict=False)

    key_id: Annotated[str, Field("", alias="kid")]
    """
    Key ID
    https://www.rfc-editor.org/rfc/rfc7515#section-4.1.4
    """

    kty: str
    """
    Identifies the cryptographic algorithm
    family used with the key, such as "RSA" or "EC"
    https://datatracker.ietf.org/doc/html/rfc7517#section-4.1
    """

    alg: str
    """
    Identifies the algorithm intended for use with the key (RSA-OAEP OR RS256)
    https://datatracker.ietf.org/doc/html/rfc7517#section-4.4
    """

    use: str
    """
    the intended use of the public key:
    - sig - signature
    - enc - encryption
    """

    n: str
    """
    Contains the modulus value for the RSA public key.
    It is represented as a Base64urlUInt-encoded value.
    https://www.rfc-editor.org/rfc/rfc7518#section-6.3
    """

    e: str
    """
    the exponent value for the RSA public key.
    It is represented as a Base64urlUInt-encoded value.
    https://www.rfc-editor.org/rfc/rfc7518#section-6.3
    """

    x5c: list[str]
    """
    X.509 Certificate Chain - Chain of certificates used for verification.
    The first entry in the array is always the cert to use for token verification.
    The other certificates can be used to verify this first certificate.
    """

    x5t: str
    """
    X.509 Certificate Thumbprint - Used to identify specific certificates
    """

    s256: str = Field("", alias="x5t#S256")


class JWKSModel(BaseModel):
    model_config = ConfigDict(strict=False)

    keys: list[JWKSKey]
