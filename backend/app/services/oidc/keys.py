import hashlib
import json
import logging
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from app.config import get_settings

logger = logging.getLogger(__name__)

_private_key: RSAPrivateKey | None = None


def get_private_key() -> RSAPrivateKey:
    global _private_key
    if _private_key is not None:
        return _private_key

    settings = get_settings()
    if settings.OIDC_RSA_PRIVATE_KEY:
        _private_key = serialization.load_pem_private_key(
            settings.OIDC_RSA_PRIVATE_KEY.encode(), password=None
        )
    else:
        logger.warning(
            "OIDC_RSA_PRIVATE_KEY not set. Auto-generating an ephemeral RSA key. "
            "This is NOT suitable for production."
        )
        _private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )

    return _private_key


def get_public_key() -> RSAPublicKey:
    return get_private_key().public_key()


def get_kid() -> str:
    public_key = get_public_key()
    jwk_dict = json.loads(
        jwt.algorithms.RSAAlgorithm.to_jwk(public_key)
    )
    canonical = json.dumps(
        {"e": jwk_dict["e"], "kty": jwk_dict["kty"], "n": jwk_dict["n"]},
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return digest[:16]


def get_jwks_document() -> dict:
    public_key = get_public_key()
    jwk_dict = json.loads(
        jwt.algorithms.RSAAlgorithm.to_jwk(public_key)
    )
    jwk_dict["kid"] = get_kid()
    jwk_dict["use"] = "sig"
    jwk_dict["alg"] = "RS256"
    return {"keys": [jwk_dict]}


def sign_jwt(payload: dict) -> str:
    private_key = get_private_key()
    kid = get_kid()
    return jwt.encode(
        payload, private_key, algorithm="RS256", headers={"kid": kid}
    )
