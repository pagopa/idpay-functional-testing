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


def internal_initiative_statistics(organization_id: str, initiative_id: str):
    """API to get initiative statistics.
        :param organization_id: ID of the organization of interest.
        :param initiative_id: ID of the initiative of interest.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.INTERNAL}{settings.IDPAY.endpoints.initiative.microservice_path}{settings.IDPAY.domain}{settings.IDPAY.endpoints.initiative.start_path}/{organization_id}{settings.IDPAY.endpoints.initiative.path}/{initiative_id}{settings.IDPAY.endpoints.initiative.end_path}',
        headers={
            'Content-Type': 'application/json',
        },
        timeout=5000)


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


def get_initiative_statistics_merchant_portal(initiative_id, merchant_id):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}/merchant/portal/initiatives/{initiative_id}/statistics',
        headers={
            'x-merchant-id': merchant_id,
        },
        timeout=settings.default_timeout
    )


def post_merchant_create_transaction_acquirer(initiative_id,
                                              amount_cents: int,
                                              merchant_id: str = 'MERCHANTID',
                                              acquirer_id: str = settings.idpay.acquirer_id,
                                              apim_request_id: str = 'APIMREQUESTID',
                                              mcc: str = '1234',
                                              merchant_fiscal_code: str = '12345678901',
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
            'idTrxAcquirer': uuid.uuid4().int,
            'initiativeId': initiative_id,
            'mcc': mcc,
            'merchantFiscalCode': merchant_fiscal_code,
            'vat': vat,
        },
    )
    return response


def get_transaction_detail(transaction_id,
                           merchant_id: str = 'MERCHANTID',
                           acquirer_id: str = settings.idpay.acquirer_id,
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
                                  acquirer_id: str = settings.idpay.acquirer_id,
                                  apim_request_id: str = 'APIMREQUESTID'
                                  ):
    response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/{transaction_id}/confirm',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': apim_request_id
        }
    )
    return response


def put_pre_authorize_payment(trx_code, token):
    response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}/{trx_code}/relate-user',
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


def delete_payment_merchant(transaction_id,
                            merchant_id: str = 'MERCHANTID',
                            acquirer_id: str = settings.idpay.acquirer_id,
                            apim_request_id: str = 'APIMREQUESTID'
                            ):
    response = requests.delete(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}{settings.IDPAY.endpoints.payment.qr_code.merchant}/{transaction_id}',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': apim_request_id
        }
    )
    return response


def delete_payment_citizen(trx_code, token):
    response = requests.delete(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.qr_code.path}/{trx_code}',
        headers={
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        }
    )
    return response


def get_merchant_unprocessed_transactions(initiative_id,
                                          merchant_id: str = 'MERCHANTID',
                                          page: int = 0
                                          ):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.transactions.merchant}{settings.IDPAY.endpoints.transactions.portal}/{initiative_id}{settings.IDPAY.endpoints.transactions.unprocessed}?page={page}&size=10',
        headers={
            'x-merchant-id': merchant_id
        },
        timeout=settings.default_timeout
    )


def get_merchant_processed_transactions(initiative_id,
                                        merchant_id: str = 'MERCHANTID',
                                        page: int = 0
                                        ):
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}{settings.IDPAY.domain}{settings.IDPAY.endpoints.transactions.merchant}{settings.IDPAY.endpoints.transactions.portal}/{initiative_id}{settings.IDPAY.endpoints.transactions.processed}?page={page}&size=10',
        headers={
            'x-merchant-id': merchant_id
        },
        timeout=settings.default_timeout
    )


def obtain_selfcare_test_token(institution_info: str):
    return requests.post(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/welfare/token/test',
        json=institution_info,
        timeout=settings.default_timeout
    )


def post_initiative_info(selfcare_token: str,
                         initiative_name_prefix: str = 'Functional test'):
    return requests.post(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/info',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json={
            'serviceIO': True,
            'serviceName': f"{initiative_name_prefix} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'serviceScope': 'LOCAL',
            'description': f'Test initiative for {initiative_name_prefix}',
            'privacyLink': 'https://www.google.it',
            'tcLink': 'https://www.google.com',
            'channels': [
                {
                    'type': 'web',
                    'contact': 'https://www.google.com'
                }
            ]
        },
        timeout=settings.default_timeout
    )


def put_initiative_general_info(selfcare_token: str,
                                initiative_id: str,
                                budget: float,
                                beneficiary_budget: float,
                                beneficiary_type: str = 'PF',
                                beneficiary_known: bool = False,
                                ranking_enabled: bool = False,
                                ranking_start_date: str = None,
                                ranking_end_date: str = None,
                                start_date: str = datetime.datetime.now().strftime('%Y-%m-%d'),
                                end_date: str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
                                    '%Y-%m-%d'),
                                description_it: str = 'it'
                                ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/general',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json={
            'budget': budget,
            'beneficiaryType': beneficiary_type,
            'beneficiaryKnown': beneficiary_known,
            'rankingEnabled': ranking_enabled,
            'beneficiaryBudget': beneficiary_budget,
            'rankingStartDate': ranking_start_date,
            'rankingEndDate': ranking_end_date,
            'startDate': start_date,
            'endDate': end_date,
            'descriptionMap': {
                'it': description_it
            }
        },
        timeout=settings.default_timeout
    )


def put_initiative_beneficiary_info(selfcare_token: str,
                                    initiative_id: str
                                    ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/beneficiary',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json={
            'automatedCriteria': [],
            'selfDeclarationCriteria': [
                {
                    '_type': 'boolean',
                    'description': '1',
                    'value': True,
                    'code': '1'
                }
            ]
        },
        timeout=settings.default_timeout
    )


def put_initiative_reward_info(selfcare_token: str,
                               initiative_id: str,
                               initiative_reward_type: str = 'DISCOUNT',
                               reward_rule_value: float = 100,
                               reward_rule_type: str = 'rewardValue',
                               reward_value_type: str = 'PERCENTAGE'
                               ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/reward',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json={
            'initiativeRewardType': initiative_reward_type,
            'rewardRule': {
                '_type': reward_rule_type,
                'rewardValue': reward_rule_value,
                'rewardValueType': reward_value_type
            },
            'trxRule': {
            }
        },
        timeout=settings.default_timeout
    )


def put_initiative_refund_info(selfcare_token: str,
                               initiative_id: str,
                               time_type: str = 'DAILY'
                               ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/refund',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json={
            'timeParameter': {
                'timeType': time_type
            }
        },
        timeout=settings.default_timeout
    )


def put_initiative_approval(selfcare_token: str,
                            initiative_id: str
                            ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/approved',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )
