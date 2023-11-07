import uuid

import requests

from conf.configuration import secrets
from conf.configuration import settings
from util.certs_loader import load_certificates


def post_merchant_create_transaction_mil(initiative_id,
                                         amount_cents: int,
                                         mcc: str = '1234',
                                         acquirer_id: str = settings.idpay.acquirer_id,
                                         merchant_fiscal_code: str = '12345678901'):
    cert = load_certificates()
    response = requests.post(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        },
        json={
            'initiativeId': initiative_id,
            'idTrxAcquirer': uuid.uuid4().int,
            'amountCents': amount_cents,
            'mcc': mcc
        }
    )
    return response


def get_initiative_list_mil(merchant_fiscal_code: str,
                            acquirer_id: str = settings.idpay.acquirer_id
                            ):
    cert = load_certificates()
    response = requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.merchant.path}/initiatives',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        }
    )
    return response


def get_transaction_detail_mil(transaction_id,
                               acquirer_id: str = settings.idpay.acquirer_id,
                               merchant_fiscal_code: str = '12345678901'
                               ):
    cert = load_certificates()
    response = requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}/{transaction_id}/status',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        }
    )
    return response


def delete_transaction_mil(transaction_id,
                           acquirer_id: str = settings.idpay.acquirer_id,
                           merchant_fiscal_code: str = '12345678901'
                           ):
    cert = load_certificates()
    response = requests.delete(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}/{transaction_id}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        }
    )
    return response


def put_merchant_pre_authorize_transaction_mil(transaction_id: str,
                                               acquirer_id: str = settings.idpay.acquirer_id,
                                               merchant_fiscal_code: str = '12345678901'):
    cert = load_certificates()
    response = requests.put(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.idpay_code.path}/{transaction_id}/preview',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        }
    )
    return response


def put_merchant_authorize_transaction_mil(transaction_id: str,
                                           pin_block: str,
                                           encrypted_key: str,
                                           acquirer_id: str = settings.idpay.acquirer_id,
                                           merchant_fiscal_code: str = '12345678901'):
    cert = load_certificates()
    response = requests.put(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.idpay_code.path}/{transaction_id}/authorize',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        },
        json={
            'pinBlock': pin_block,
            'encryptedKey': encrypted_key
        }
    )
    return response


def get_public_key(acquirer_id: str = settings.idpay.acquirer_id):
    cert = load_certificates()
    response = requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}/publickey',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-acquirer-id': acquirer_id
        }
    )
    return response
