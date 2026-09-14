import base64
import datetime
import json
import random
import uuid


def generate_merchant_name():
    return f"Esercente di test {datetime.datetime.now().strftime("%Y%m%d - %H%M%S")} {str(uuid.uuid4())[:4]}"


def generate_merchant_vat():
    return str(random.randint(10000000000, 99999999999))


def decode_jwt_payload(token: str) -> dict:
    """Decode a JWT payload without verifying its signature."""
    parts = token.split(".")
    if len(parts) < 3:
        raise ValueError("Token must contain header.payload.signature segments.")

    payload_segment = parts[1]
    padded_segment = payload_segment + "=" * (-len(payload_segment) % 4)
    decoded_bytes = base64.urlsafe_b64decode(padded_segment.encode("ascii"))
    return json.loads(decoded_bytes.decode("utf-8"))
