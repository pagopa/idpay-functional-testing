import datetime
import uuid

import requests

from conf.configuration import settings
from util.certs_loader import load_certificates
from util.dataset_utility import tomorrow_date


def timeline(initiative_id, token, page: int = 1):
    """API to get timeline of a user
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param page: page to query.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.timeline.path}/{initiative_id}/?page={page}&size=10',
        headers={
            'Authorization': f'Bearer {token}',
        },
        timeout=settings.default_timeout
    )


def wallet(initiative_id, token):
    """API to get citizen wallet.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)


def unsubscribe(initiative_id, token):
    """API to unsubscribe a citizen from an initiative.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.delete(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.unsubscribe}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)


def enroll_iban(initiative_id, token, body):
    """API to enroll an IBAN
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param body: JSON of IBAN and its description.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.start_path}/{initiative_id}{settings.IDPAY.endpoints.onboarding.iban.end_path}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=body,
        timeout=settings.default_timeout)


def get_payment_instruments(initiative_id, token):
    """API to get payment instruments.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.end_path}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=settings.default_timeout)


def get_iban_list(token):
    """API to get list of IBANs associated to a citizen.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.end_path}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=settings.default_timeout)


def get_iban_info(iban, token):
    """API to get information about an IBAN enrolled by a citizen.
        :param iban: IBAN of interest.
        :param token: token IO.
    """
    cert = load_certificates()
    return requests.get(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.iban.end_path}/{iban}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=settings.default_timeout)


def remove_payment_instrument(initiative_id, token, instrument_id):
    """API to remove payment instrument by instrument ID.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param instrument_id: ID of the card to remove.
    """
    cert = load_certificates()
    return requests.delete(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.end_path}/{instrument_id}',
        cert=cert,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it_IT',
        },
        timeout=settings.default_timeout)


def force_reward():
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.rewards.path}{settings.IDPAY.endpoints.rewards.force_reward}{tomorrow_date()}',
        timeout=settings.long_timeout
    )


def get_reward_content(organization_id, initiative_id, export_id):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.rewards.path}/organization/{organization_id}/initiative/{initiative_id}/reward/notification/exports/{export_id}/content',
        timeout=settings.default_timeout
    )


def get_initiative_statistics(organization_id, initiative_id):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}/organization/{organization_id}/initiative/{initiative_id}/statistics',
        timeout=settings.default_timeout
    )


def post_merchant_create_transaction_acquirer(initiative_id,
                                              amount_cents: int,
                                              merchant_id: str = 'MERCHANTID',
                                              acquirer_id: str = 'ACQUIRERID',
                                              apim_request_id: str = 'APIMREQUESTID',
                                              mcc: str = '1234',
                                              merchant_fiscal_code: str = '12345678901',
                                              trx_date: datetime = tomorrow_date(is_iso=True),
                                              vat: str = '12345678901'):
    response = requests.post(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': apim_request_id,
        },
        json={
            'amountCents': amount_cents,
            'idTrxIssuer': uuid.uuid4().int,
            'initiativeId': initiative_id,
            'mcc': mcc,
            'merchantFiscalCode': merchant_fiscal_code,
            'trxDate': trx_date,
            'vat': vat,
        },
    )
    return response


def get_transaction_detail(transaction_id,
                           merchant_id: str = 'MERCHANTID',
                           acquirer_id: str = 'ACQUIRERID',
                           ):
    response = requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/status/{transaction_id}',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': 'TEST',
        }
    )
    return response


def put_merchant_confirms_payment(transaction_id,
                                  merchant_id: str = 'MERCHANTID',
                                  acquirer_id: str = 'ACQUIRERID',
                                  api_request_id: str = 'TEST'
                                  ):
    response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/{transaction_id}/confirm',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': api_request_id
        }
    )
    return response


def put_pre_authorize_payment(trx_code, token):
    response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{trx_code}/relate-user',
        headers={
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        }
    )
    return response


def put_authorize_payment(trx_code, token):
    response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}/{trx_code}/authorize',
        headers={
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        }
    )
    return response
