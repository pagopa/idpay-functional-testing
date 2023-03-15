"""Utility class that loads mutual authentication certificate and keys from base64 to file.
"""
import base64
import tempfile

from conf.configuration import secrets


def load_certificates():
    """Decode cert and key in base64 from secrets to file.
        """
    cert = base64.b64decode(secrets.mauth.cert_base64)
    key = base64.b64decode(secrets.mauth.key_base64)

    with tempfile.NamedTemporaryFile(delete=False) as cert_file:
        cert_file.write(cert)
    cert_file.close()
    with tempfile.NamedTemporaryFile(delete=False) as key_file:
        key_file.write(key)
    key_file.close()

    return cert_file.name, key_file.name


def load_pm_public_key():
    """Decode PM public key in base64 from secrets.
    """
    return base64.b64decode(secrets.pm.pub_key).decode('utf-8')
