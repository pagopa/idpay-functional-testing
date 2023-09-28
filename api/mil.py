import uuid

import requests

from conf.configuration import secrets
from conf.configuration import settings
from util.certs_loader import load_certificates


def post_merchant_create_transaction_acquirer_mil(initiative_id,
                                                  amount_cents: int,
                                                  mcc: str = '1234',
                                                  acquirer_id: str = settings.idpay.acquirer_id,
                                                  merchant_fiscal_code: str = '12345678901'):
    cert = load_certificates()
    response = requests.post(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-acquirer-id': acquirer_id,
            'x-merchant-fiscalcode': merchant_fiscal_code
        },
        json={
            'initiativeId': initiative_id,
            'merchantFiscalCode': merchant_fiscal_code,
            'idTrxAcquirer': uuid.uuid4().int,
            'amountCents': amount_cents,
            'mcc': mcc,
        },
    )
    return response


def get_initiative_list_mil(merchant_fiscal_code: str,
                            acquirer_id: str = settings.idpay.acquirer_id
                            ):
    cert = load_certificates()
    response = requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/initiatives',
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
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/status/{transaction_id}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id,
        }
    )
    return response


def delete_transaction_mil(transaction_id,
                           acquirer_id: str = settings.idpay.acquirer_id,
                           merchant_fiscal_code: str = '12345678901'
                           ):
    cert = load_certificates()
    response = requests.delete(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.MIL.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/{transaction_id}',
        cert=cert,
        headers={
            settings.API_KEY_HEADER: secrets.api_key.IDPAY_MIL_PRODUCT,
            'x-merchant-fiscalcode': merchant_fiscal_code,
            'x-acquirer-id': acquirer_id
        }
    )
    return response
