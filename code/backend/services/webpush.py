"""Minimal Web Push sender (plan 5.5): RFC 8291 message encryption (aes128gcm,
RFC 8188) + RFC 8292 VAPID, on top of `cryptography`.

Why not pywebpush: its dependency http-ece ships only an sdist whose setup.py no
longer builds with current setuptools (checked 2026-11-02) - it would break
`pip install` in Docker and on Windows. The encryption is verified against the
RFC 8291 Appendix A test vector in tests/test_webpush.py.
"""
import base64
import json
import os
import struct
import time
from urllib.parse import urlparse

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

RECORD_SIZE = 4096


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _public_bytes(key: ec.EllipticCurvePublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def _hkdf(salt: bytes, ikm: bytes, info: bytes, length: int) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info).derive(ikm)


def encrypt(plaintext: bytes, ua_public: bytes, auth_secret: bytes,
            as_private: ec.EllipticCurvePrivateKey | None = None, salt: bytes | None = None) -> bytes:
    """aes128gcm body for one Web Push message (RFC 8291 §3.4, single record).

    `as_private` and `salt` are only passed by the RFC test vector; normally fresh."""
    as_private = as_private or ec.generate_private_key(ec.SECP256R1())
    salt = salt or os.urandom(16)
    as_public = _public_bytes(as_private.public_key())
    ua_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), ua_public)

    ecdh_secret = as_private.exchange(ec.ECDH(), ua_key)
    key_info = b"WebPush: info\x00" + ua_public + as_public
    ikm = _hkdf(auth_secret, ecdh_secret, key_info, 32)
    cek = _hkdf(salt, ikm, b"Content-Encoding: aes128gcm\x00", 16)
    nonce = _hkdf(salt, ikm, b"Content-Encoding: nonce\x00", 12)

    record = plaintext + b"\x02"  # last-record delimiter, no padding
    if len(record) + 16 > RECORD_SIZE:
        raise ValueError("Push message too long")
    ciphertext = AESGCM(cek).encrypt(nonce, record, None)
    header = salt + struct.pack("!IB", RECORD_SIZE, len(as_public)) + as_public
    return header + ciphertext


def load_vapid_private(raw_b64url: str) -> ec.EllipticCurvePrivateKey:
    return ec.derive_private_key(int.from_bytes(b64url_decode(raw_b64url), "big"), ec.SECP256R1())


def generate_vapid_keys() -> dict[str, str]:
    key = ec.generate_private_key(ec.SECP256R1())
    private_raw = key.private_numbers().private_value.to_bytes(32, "big")
    return {"VAPID_PRIVATE_KEY": b64url_encode(private_raw), "VAPID_PUBLIC_KEY": b64url_encode(_public_bytes(key.public_key()))}


def vapid_header(endpoint: str, private_key: ec.EllipticCurvePrivateKey, subject: str,
                 now: int | None = None) -> str:
    """RFC 8292: `vapid t=<JWT ES256>, k=<public key>`."""
    url = urlparse(endpoint)
    claims = {"aud": f"{url.scheme}://{url.netloc}", "exp": int(now or time.time()) + 12 * 3600, "sub": subject}
    signing_input = (
        b64url_encode(json.dumps({"typ": "JWT", "alg": "ES256"}, separators=(",", ":")).encode())
        + "."
        + b64url_encode(json.dumps(claims, separators=(",", ":")).encode())
    )
    der = private_key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    public = b64url_encode(_public_bytes(private_key.public_key()))
    return f"vapid t={signing_input}.{b64url_encode(signature)}, k={public}"


class SubscriptionGone(Exception):
    """404/410 from the push service: the browser unsubscribed - delete it."""


def send(subscription: dict, payload: dict, private_key: ec.EllipticCurvePrivateKey, subject: str,
         post=httpx.post, ttl: int = 12 * 3600) -> None:
    """subscription: {"endpoint", "keys": {"p256dh", "auth"}} as the browser gives it."""
    body = encrypt(
        json.dumps(payload, ensure_ascii=False).encode(),
        b64url_decode(subscription["keys"]["p256dh"]),
        b64url_decode(subscription["keys"]["auth"]),
    )
    headers = {
        "Authorization": vapid_header(subscription["endpoint"], private_key, subject),
        "Content-Encoding": "aes128gcm",
        "Content-Type": "application/octet-stream",
        "TTL": str(ttl),
        "Urgency": "normal",
    }
    response = post(subscription["endpoint"], content=body, headers=headers, timeout=10)
    if response.status_code in (404, 410):
        raise SubscriptionGone
    response.raise_for_status()
