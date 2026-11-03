import datetime
import uuid

import requests

from conf.configuration import secrets
from conf.configuration import settings


def timeline(initiative_id, token, page: int = 0):
    """API to get timeline of a user
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :param page: page to query.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.timeline.path}/{initiative_id}/?page={page}&size=10',
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
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept-Language': 'it-IT'
        },
        timeout=settings.default_timeout)


def get_initiative_statistics(organization_id, initiative_id):
    res = requests.get(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}/organization/{organization_id}/initiative/{initiative_id}/statistics',
        timeout=settings.default_timeout
    )
    return res


def get_initiative_statistics_merchant_portal(initiative_id, merchant_id):
    return requests.get(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.statistics.path}{settings.IDPAY.endpoints.merchant.path}/portal/initiatives/{initiative_id}/statistics',
        headers={
            'x-merchant-id': merchant_id,
        },
        timeout=settings.default_timeout
    )


def get_transaction_detail(transaction_id,
                           merchant_id: str = 'MERCHANTID',
                           acquirer_id: str = settings.idpay.acquirer_id
                           ):
    response = requests.get(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.payment.internal_path}{settings.IDPAY.endpoints.payment.path}/{transaction_id}/status',
        headers={
            'x-merchant-id': merchant_id,
            'x-acquirer-id': acquirer_id
        }
    )
    return response


def get_merchant_processed_transactions(initiative_id,
                                        merchant_id: str = 'MERCHANTID',
                                        page: int = 0,
                                        size: int = 10,
                                        reward_batch_id: str | None = None,
                                        reward_batch_trx_status: str | None = None,
                                        *,
                                        access_token: str
                                        ):
    params = {
        'page': page,
        'size': size
    }
    if reward_batch_id is not None:
        params['rewardBatchId'] = reward_batch_id
    if reward_batch_trx_status is not None:
        params['rewardBatchTrxStatus'] = reward_batch_trx_status

    return requests.get(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.transactions.merchant}{settings.IDPAY.endpoints.transactions.portal}/{initiative_id}{settings.IDPAY.endpoints.transactions.processed}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'x-merchant-id': merchant_id
        },
        params=params,
        timeout=settings.default_timeout
    )


def get_reward_batch_eligibility(transaction_id: str,
                                 merchant_id: str,
                                 access_token: str):
    return requests.get(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}/idpay/transactions/{transaction_id}{settings.IDPAY.endpoints.transactions.reward_batch_eligibility}',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        params={
            'merchantId': merchant_id
        },
        timeout=settings.default_timeout
    )


def post_prepare_reward_batch_for_send(initiative_id: str,
                                       reward_batch_id: str):
    return requests.post(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}'
        f'{settings.IDPAY.endpoints.transactions.reward_batch_test_support}/{initiative_id}'
        f'/reward-batches/{reward_batch_id}/prepare-for-send',
        timeout=settings.default_timeout
    )


def post_send_reward_batch(initiative_id: str,
                           reward_batch_id: str,
                           access_token: str):
    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.transactions.merchant}'
        f'{settings.IDPAY.endpoints.transactions.portal}/{initiative_id}'
        f'/reward-batches/{reward_batch_id}/send',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        timeout=settings.default_timeout
    )


def post_evaluate_sent_reward_batches(initiative_id: str,
                                      reward_batch_ids: list[str] | None = None):
    payload = {} if reward_batch_ids is None else {'rewardBatchIds': reward_batch_ids}
    return requests.post(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}'
        f'{settings.IDPAY.endpoints.transactions.reward_batches}/{initiative_id}'
        f'/reward-batches/evaluate',
        json=payload,
        timeout=settings.default_timeout
    )


def get_reward_batch_detail(initiative_id: str,
                            reward_batch_id: str,
                            merchant_id: str):
    return requests.get(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}'
        f'{settings.IDPAY.endpoints.transactions.reward_batches}/{initiative_id}'
        f'/reward-batches/{reward_batch_id}',
        headers={
            'x-merchant-id': merchant_id
        },
        timeout=settings.default_timeout
    )


def obtain_selfcare_test_token(institution_info: str):
    return requests.post(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/welfare/token/test',
        json=institution_info,
        timeout=settings.default_timeout
    )


def obtain_merchant_test_token(merchant_info: dict):
    return requests.post(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/merchant/token/test',
        json=merchant_info,
        timeout=settings.default_timeout
    )


def post_initiative_info(selfcare_token: str,
                         initiative_name_prefix: str = 'Functional test'):
    return requests.post(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/info',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json'
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
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/general',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json'
        },
        json=general_payload,
        timeout=settings.default_timeout
    )


def put_initiative_beneficiary_info(selfcare_token: str,
                                    initiative_id: str,
                                    beneficiary_payload: str
                                    ):
    return requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/beneficiary',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json'
        },
        json=beneficiary_payload,
        timeout=settings.default_timeout
    )


def put_initiative_reward_info(selfcare_token: str,
                               initiative_id: str,
                               reward_payload: str
                               ):
    return requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/reward',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json'
        },
        json=reward_payload,
        timeout=settings.default_timeout
    )


def put_initiative_refund_info(selfcare_token: str,
                               initiative_id: str,
                               refund_payload: str
                               ):
    return requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/refund',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
            'Content-Type': 'application/json'
        },
        json=refund_payload,
        timeout=settings.default_timeout
    )


def put_initiative_approval(selfcare_token: str,
                            initiative_id: str
                            ):
    return requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/approved',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def publish_approved_initiative(selfcare_token: str,
                                initiative_id: str
                                ):
    return requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/{initiative_id}/published',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def get_initiatives_summary(selfcare_token: str
                            ):
    return requests.get(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/initiative/summary',
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def delete_initiative(initiative_id: str, domain: str = None):
    """API to delete everything related to an initiative.
            :param initiative_id: ID of the initiative of interest.
            :param domain: Internal backend domain, when different from the gateway domain.
            :returns: the response of the call.
            :rtype: requests.Response
        """
    return requests.delete(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.initiatives.portal}{domain or settings.IDPAY.domain}/initiative/{initiative_id}',
        timeout=settings.default_timeout)


def post_create_payment_bar_code(token, initiative_id: str):
    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.payment.path}{settings.IDPAY.endpoints.payment.bar_code.path}',
        headers={
            'Authorization': f'Bearer {token}',
            'accept': 'application/json'
        },
        json={
            'initiativeId': initiative_id
        }
    )


def put_authorize_bar_code_merchant(trx_code: str,
                                    amount_cents: int,
                                    initiative_id: str,
                                    access_token: str = None,
                                    additional_properties=None
                                    ):
    headers = {
        'Content-Type': 'application/json'
    }
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    payload = {
        'amountCents': amount_cents,
        'idTrxAcquirer': str(uuid.uuid4())
    }
    if additional_properties:
        payload['additionalProperties'] = additional_properties

    return requests.put(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.ecommerce.path}/initiatives/{initiative_id}/{settings.IDPAY.endpoints.ecommerce.barcode}/{trx_code}{settings.IDPAY.endpoints.ecommerce.authorize}',
        headers=headers,
        json=payload
    )


def put_capture_bar_code_merchant(trx_code: str, access_token: str, initiative_id: str):
    return requests.put(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.ecommerce.path}'
        f'/initiatives/{initiative_id}{settings.IDPAY.endpoints.ecommerce.barcode}/{trx_code}'
        f'{settings.IDPAY.endpoints.ecommerce.capture}',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )


def delete_transaction_bar_code_merchant(initiative_id: str,
                                        transaction_id: str,
                                        access_token: str):
    return requests.delete(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.ecommerce.path}'
        f'/initiatives/{initiative_id}/transactions/{transaction_id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        timeout=settings.default_timeout
    )


def post_invoice_bar_code_merchant(initiative_id: str,
                                   transaction_id: str,
                                   access_token: str,
                                   invoice_content: bytes,
                                   doc_number: str,
                                   filename: str = 'invoice.pdf'):
    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.ecommerce.path}'
        f'/initiatives/{initiative_id}/transactions/{transaction_id}'
        f'{settings.IDPAY.endpoints.ecommerce.invoice}',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        data={
            'docNumber': doc_number
        },
        files={
            'file': (filename, invoice_content, 'application/pdf')
        },
        timeout=settings.default_timeout
    )


def put_invoice_bar_code_as_merchant(initiative_id: str,
                                     transaction_id: str,
                                     access_token: str,
                                     invoice_content: bytes,
                                     doc_number: str,
                                     filename: str = 'invoice.pdf'):
    return requests.put(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.ecommerce.merchant_portal}'
        f'/initiatives/{initiative_id}/transactions/{transaction_id}'
        f'{settings.IDPAY.endpoints.ecommerce.invoice}/update',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        data={
            'docNumber': doc_number
        },
        files={
            'file': (filename, invoice_content, 'application/pdf')
        },
        timeout=settings.default_timeout
    )


def post_reversal_bar_code_merchant(initiative_id: str,
                                    transaction_id: str,
                                    access_token: str,
                                    reversal_content: bytes,
                                    doc_number: str):
    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.ecommerce.path}/initiatives/{initiative_id}/transactions/{transaction_id}{settings.IDPAY.endpoints.ecommerce.reversal}',
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        data={
            'docNumber': doc_number
        },
        files={
            'file': ('reversal.pdf', reversal_content, 'application/pdf')
        },
        timeout=settings.default_timeout
    )


def upload_whitelist_csv(selfcare_token: str,
                         initiative_id: str,
                         whitelist_payload: dict):
    res = requests.put(
        url=f'{secrets.base_path.IO}{settings.IDPAY.domain}/group/initiative/{initiative_id}/upload',
        files=whitelist_payload,
        headers={
            'Authorization': f'Bearer {selfcare_token}'
        },
        timeout=settings.default_timeout
    )

    return res


def unsubscribe(initiative_id, token):
    """API to unsubscribe a citizen from an initiative.
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.delete(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.wallet.path}/{initiative_id}{settings.IDPAY.endpoints.wallet.unsubscribe}',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=settings.default_timeout)
