"""Plan 5.5: Web Push encryption checked against RFC 8291 Appendix A, VAPID signature verifiable."""
import json

import httpx
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from backend.services import webpush
from backend.services.webpush import b64url_decode, b64url_encode

# RFC 8291, Appendix A
PLAINTEXT = b"When I grow up, I want to be a watermelon"
AS_PRIVATE = "yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw"
UA_PUBLIC = "BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4"
AUTH_SECRET = "BTBZMqHH6r4Tts7J_aSIgg"
SALT = "DGv6ra1nlYgDCS1FRnbzlw"
EXPECTED = (
    "DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A_"
    "yl95bQpu6cVPTpK4Mqgkf1CXztLVBSt2Ks3oZwbuwXPXLWyouBWLVWGNWQexSgSxsj_Qulcy4a-fN"
)


def test_encrypt_matches_rfc8291_vector():
    body = webpush.encrypt(
        PLAINTEXT, b64url_decode(UA_PUBLIC), b64url_decode(AUTH_SECRET),
        as_private=webpush.load_vapid_private(AS_PRIVATE), salt=b64url_decode(SALT),
    )
    assert b64url_encode(body) == EXPECTED


def test_vapid_jwt_is_verifiable():
    keys = webpush.generate_vapid_keys()
    private = webpush.load_vapid_private(keys["VAPID_PRIVATE_KEY"])
    header = webpush.vapid_header("https://fcm.googleapis.com/fcm/send/abc", private, "mailto:me@example.com", now=1000)
    token = header.split("t=")[1].split(",")[0]
    k = header.split("k=")[1]
    head, claims, sig = token.split(".")
    assert json.loads(b64url_decode(claims)) == {"aud": "https://fcm.googleapis.com", "exp": 1000 + 43200,
                                                 "sub": "mailto:me@example.com"}
    raw = b64url_decode(sig)
    der = encode_dss_signature(int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big"))
    public = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), b64url_decode(k))
    public.verify(der, f"{head}.{claims}".encode(), ec.ECDSA(hashes.SHA256()))  # raises if invalid
    assert k == keys["VAPID_PUBLIC_KEY"]


def _subscription():
    ua = ec.generate_private_key(ec.SECP256R1())
    from cryptography.hazmat.primitives import serialization
    pub = ua.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return {"endpoint": "https://push.example.com/x", "keys": {"p256dh": b64url_encode(pub), "auth": b64url_encode(b"0123456789abcdef")}}


def test_send_posts_encrypted_body_and_handles_gone():
    keys = webpush.generate_vapid_keys()
    private = webpush.load_vapid_private(keys["VAPID_PRIVATE_KEY"])
    seen = {}

    def post(url, content, headers, timeout):
        seen.update(url=url, headers=headers, size=len(content))
        return httpx.Response(201, request=httpx.Request("POST", url))

    webpush.send(_subscription(), {"title": "Pielęgnacja"}, private, "mailto:me@example.com", post=post)
    assert seen["headers"]["Content-Encoding"] == "aes128gcm" and seen["headers"]["Authorization"].startswith("vapid t=")
    assert seen["size"] > 86

    def gone(url, content, headers, timeout):
        return httpx.Response(410, request=httpx.Request("POST", url))

    with pytest.raises(webpush.SubscriptionGone):
        webpush.send(_subscription(), {"title": "x"}, private, "mailto:me@example.com", post=gone)
