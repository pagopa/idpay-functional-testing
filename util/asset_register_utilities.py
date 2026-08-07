import random

from conf.configuration import secrets
from model.asset_register_model import AssetRegisterTokenPayload

def _get_token_payload_from_secrets(profile: str) -> dict[str, str]:
    asset_register_secrets = getattr(secrets, "asset_register", None)
    if asset_register_secrets is None:
        raise KeyError("Missing secrets.asset_register configuration")

    token_payloads = getattr(asset_register_secrets, "token_payload", None)
    if token_payloads is None:
        raise KeyError("Missing secrets.asset_register.token_payload configuration")

    payload = token_payloads.get(profile)
    if payload is None:
        raise KeyError(f"Missing secrets.asset_register.token_payload.{profile} configuration")

    return payload

def _build_asset_register_token_payload(profile: str) -> AssetRegisterTokenPayload:
    payload = _get_token_payload_from_secrets(profile=profile)
    return AssetRegisterTokenPayload.from_dict(payload)


def _build_asset_register_token_body(profile: str) -> dict[str, str]:
    return _build_asset_register_token_payload(profile=profile).to_dict()


def build_l1_token_body() -> dict[str, str]:
    return _build_asset_register_token_body(profile="l1")


def build_l2_token_body() -> dict[str, str]:
    return _build_asset_register_token_body(profile="l2")


def build_operatore_token_body() -> dict[str, str]:
    return _build_asset_register_token_body(profile="operatore")

def fake_product_file(row_number: int = 1):
    header = "Codice EPREL;Codice GTIN/EAN;Codice Prodotto;Categoria;Paese di Produzione"
    fake_csv_file = [header]

    for _ in range(row_number):
        eprel_code = random.randint(1000000, 9999999)
        gtin_code = random.randint(100000, 999999)
        product_code = random.randint(100000000, 999999999)
        fake_csv_file.append(f"{eprel_code};{gtin_code};{product_code};TUMBLEDRYERS;IT")

    csv_content = '\n'.join(fake_csv_file).encode('utf-8')
    csv_file = ('test.csv', csv_content, 'text/csv')
    return csv_file

def _build_csv_file_part(csv_file):
    if isinstance(csv_file, tuple):
        return csv_file

    if isinstance(csv_file, dict):
        if 'name' in csv_file and 'content' in csv_file:
            return csv_file['name'], csv_file['content'], 'text/csv'
        if 'file' in csv_file:
            return csv_file['file']

    raise TypeError(
        "csv_file must be a tuple (filename, content[, content_type]) or "
        "a dict with keys {'name','content'} or {'file': (...)}"
    )