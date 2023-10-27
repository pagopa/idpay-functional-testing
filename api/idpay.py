import datetime
import uuid

import requests

from conf.configuration import settings
from util.certs_loader import load_certificates
from util.dataset_utility import tomorrow_date
from util.dataset_utility import yesterday_date


def timeline(initiative_id, token, page: int = 0):
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
    res = requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}/organization/{organization_id}/initiative/{initiative_id}/statistics',
        timeout=settings.default_timeout
    )
    return res


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
                           acquirer_id: str = settings.idpay.acquirer_id
                           ):
    response = requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}/{transaction_id}/status',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id,
            'x-apim-request-id': 'TEST',
        }
    )
    return response


def put_merchant_confirms_payment(transaction_id,
                                  merchant_id: str = 'MERCHANTID',
                                  acquirer_id: str = settings.idpay.acquirer_id
                                  ):
    response = requests.put(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.payment.path}/{transaction_id}/confirm',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id
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
                            acquirer_id: str = settings.idpay.acquirer_id
                            ):
    response = requests.delete(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.payment.path}/{transaction_id}',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id
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
                                general_payload: str):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/general',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json=general_payload,
        timeout=settings.default_timeout
    )


def put_initiative_beneficiary_info(selfcare_token: str,
                                    initiative_id: str,
                                    beneficiary_payload: str
                                    ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/beneficiary',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json=beneficiary_payload,
        timeout=settings.default_timeout
    )


def put_initiative_reward_info(selfcare_token: str,
                               initiative_id: str,
                               reward_payload: str
                               ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/reward',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json=reward_payload,
        timeout=settings.default_timeout
    )


def put_initiative_refund_info(selfcare_token: str,
                               initiative_id: str,
                               refund_payload: str
                               ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/refund',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        json=refund_payload,
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


def publish_approved_initiative(selfcare_token: str,
                                initiative_id: str
                                ):
    return requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/published',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def get_initiatives_summary(selfcare_token: str
                            ):
    return requests.get(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/summary',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def upload_merchant_csv(selfcare_token: str,
                        initiative_id: str,
                        merchants_payload: dict):
    res = requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/merchant/initiative/{initiative_id}/upload',
        files=merchants_payload,
        headers={
            'Authorization': f'Bearer {selfcare_token}'
        },
        timeout=settings.default_timeout
    )

    return res


def get_merchant_list(organization_id: str,
                      initiative_id: str,
                      page: int = 0):
    """API to get initiative statistics.
        :param organization_id: ID of the organization of interest.
        :param initiative_id: ID of the initiative of interest.
        :param page: Page of merchants to query.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.merchant.path}{settings.IDPAY.domain}/merchant/organization/{organization_id}/initiative/{initiative_id}/merchants?page={page}',
        headers={
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout
    )


def delete_initiative(initiative_id: str):
    """API to delete everything related to an initiative.
            :param initiative_id: ID of the initiative of interest.
            :returns: the response of the call.
            :rtype: requests.Response
        """
    return requests.delete(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.initiatives.portal}{settings.IDPAY.domain}/initiative/{initiative_id}',
        timeout=settings.default_timeout)


def put_citizen_suspension(selfcare_token: str,
                           initiative_id: str,
                           fiscal_code: str):
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/{settings.IDPAY.endpoints.initiatives.beneficiary.path}{settings.IDPAY.endpoints.initiatives.beneficiary.suspend}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Fiscal-Code': f'{fiscal_code}',
        },
        timeout=settings.default_timeout
    )


def get_payment_dispositions_export_content(selfcare_token: str,
                                            initiative_id: str,
                                            exported_file_name: str):
    """API to get the desired export file.
        :param selfcare_token: Self-Care token of the test organization that should download the exports.
        :param initiative_id: ID of the initiative of interest.
        :param exported_file_name: Name of the export file.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    res = requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/reward/exports/{exported_file_name}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'accept': 'application/json'
        },
        timeout=settings.default_timeout
    )
    return res


def put_citizen_readmission(selfcare_token: str,
                            initiative_id: str,
                            fiscal_code: str):
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/{settings.IDPAY.endpoints.initiatives.beneficiary.path}{settings.IDPAY.endpoints.initiatives.beneficiary.readmit}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Fiscal-Code': f'{fiscal_code}',
        },
        timeout=settings.default_timeout
    )


def put_ranking_end_date(initiative_id: str):
    res = requests.put(
        url=f'{settings.base_path.IDPAY.internal}/idpayranking{settings.IDPAY.domain}/initiative/{initiative_id}/reset-status-set-ranking-end-date?rankingEndDate={yesterday_date()}',
        timeout=settings.default_timeout
    )
    return res


def force_ranking():
    res = requests.get(
        url=f'{settings.base_path.IDPAY.internal}/idpayranking{settings.IDPAY.domain}/ranking/build/file/start',
        timeout=settings.default_timeout
    )
    return res


def get_ranking_file(selfcare_token: str, initiative_id: str, ranking_file_path: str):
    res = requests.get(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/ranking/exports/{ranking_file_path}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )
    return res


def get_ranking_page(selfcare_token: str,
                     initiative_id: str,
                     page: int = 0):
    res = requests.get(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/ranking/exports?page={page}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )
    return res


def put_publish_ranking(selfcare_token: str, initiative_id: str):
    res = requests.put(
        url=f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/ranking/notified',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )
    return res


def post_idpay_code_generate(token: str, body: dict = None):
    return requests.post(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}{settings.IDPAY.endpoints.wallet.code_generate}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=body,
        timeout=settings.default_timeout)


def get_idpay_code_status(token: str):
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}{settings.IDPAY.endpoints.wallet.code_status}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)


def put_code_instrument(token: str, initiative_id: str):
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.code_instruments}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)


def put_payment_results(selfcare_token: str,
                        initiative_id: str,
                        results_file_name: str,
                        results_file):
    return requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/reward/import/{results_file_name}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'accept': 'application/json'
        },
        data=results_file,
        timeout=settings.default_timeout
    )


def post_create_payment_bar_code(token, initiative_id: str):
    return requests.post(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.bar_code.path}',
        headers={
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        },
        json={
            'initiativeId': initiative_id
        }
    )


def put_authorize_bar_code_merchant(merchant_id: str,
                                    trx_code: str,
                                    amount_cents: int,
                                    acquirer_id: str = settings.idpay.acquirer_id
                                    ):
    return requests.put(
        f'{settings.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.bar_code.path}/{trx_code}/authorize',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id
        },
        json={
            'amountCents': amount_cents,
            'idTrxAcquirer': uuid.uuid4().int
        }
    )

  
def get_initiative_info(selfcare_token: str,
                        initiative_id: str):
    """API to get information related to an initiative.
            :param selfcare_token: token SelfCare.
            :param initiative_id: ID of the initiative of interest.
            :returns: the response of the call.
            :rtype: requests.Response
        """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)
