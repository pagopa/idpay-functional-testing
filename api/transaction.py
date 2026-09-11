import time

import requests

from conf.configuration import secrets
from conf.configuration import settings
from model.transaction_model import ReportRequest
from model.transaction_model import TransactionActionRequest


def _reward_batch_base_path(initiative_id: str, reward_batch_id: str) -> str:
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return (
        f"{secrets.base_path.IO}{settings.IDPAY.domain}"
        f"{settings.IDPAY.endpoints.transactions.merchant}"
        f"/initiatives/{initiative_id}"
        f"{reward_batch.path}/{reward_batch_id}"
    )


def get_merchant_transactions_processed(
        merchant_id: str,
        initiative_id: str,
        access_token: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None,
        fiscal_code: str | None = None,
        status: str | None = None,
        reward_batch_id: str | None = None,
        reward_batch_trx_status: str | None = None,
        point_of_sale_id: str | None = None,
        trx_code: str | None = None):
    """API to get processed transactions for a merchant and initiative.
        GET /merchant/{merchantId}/initiative/{initiativeId}/transactions/processed
        parameters:
        page: page number
        size: page size
        sort: sort order
        fiscal_code: fiscal code
        status: transaction status
        reward_batch_id: reward batch id
        reward_batch_trx_status: reward batch transaction status
        point_of_sale_id: point of sale id
        trx_code: transaction code
    """
    params = {}
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size
    if sort is not None:
        params['sort'] = sort
    if fiscal_code is not None:
        params['fiscalCode'] = fiscal_code
    if status is not None:
        params['status'] = status
    if reward_batch_id is not None:
        params['rewardBatchId'] = reward_batch_id
    if reward_batch_trx_status is not None:
        params['rewardBatchTrxStatus'] = reward_batch_trx_status
    if point_of_sale_id is not None:
        params['pointOfSaleId'] = point_of_sale_id
    if trx_code is not None:
        params['trxCode'] = trx_code

    headers = {}
    if access_token is not None:
        headers['Authorization'] = f"Bearer {access_token}"

    return requests.get(
        f"{secrets.base_path.IO}{settings.IDPAY.domain}"
        f"{settings.IDPAY.endpoints.merchant.path}/{merchant_id}"
        f"/initiative/{initiative_id}"
        f"{settings.IDPAY.endpoints.transactions.processed}",
        headers=headers,
        params=params,
        timeout=settings.default_timeout
    )


def post_approve_transactions(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str,
        transaction_action_request: TransactionActionRequest):
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.post(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.transactions.approved}",
        headers={
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
        },
        json=(
            transaction_action_request.to_dict()
        ),
        timeout=settings.default_timeout
    )


def post_approve_reward_batch(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str):
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.post(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.approved}",
        headers={
            'Authorization': f"Bearer {access_token}",
        },
        timeout=settings.default_timeout
    )


def get_approved_reward_batch_download(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str,
        wait_seconds: float | int = 0):
    if wait_seconds:
        time.sleep(float(wait_seconds))
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.get(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.approved}/download",
        headers={
            'Authorization': f"Bearer {access_token}",
        },
        timeout=settings.default_timeout
    )


def post_validate_reward_batch(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str):
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.post(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.validated}",
        headers={
            'Authorization': f"Bearer {access_token}",
        },
        timeout=settings.default_timeout
    )


def post_reject_transactions(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str,
        transaction_action_request: TransactionActionRequest):
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.post(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.transactions.rejected}",
        headers={
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
        },
        json=(
            transaction_action_request.to_dict()
        ),
        timeout=settings.default_timeout
    )


def post_suspend_transactions(
        initiative_id: str,
        reward_batch_id: str,
        access_token: str,
        transaction_action_request: TransactionActionRequest):
    reward_batch = settings.IDPAY.endpoints.transactions.reward_batch
    return requests.post(
        f"{_reward_batch_base_path(initiative_id, reward_batch_id)}"
        f"{reward_batch.transactions.suspended}",
        headers={
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
        },
        json=(
            transaction_action_request.to_dict()
        ),
        timeout=settings.default_timeout
    )


def get_reward_batches(
        initiative_id: str,
        status: str | None = None,
        assignee_level: str | None = None,
        month: str | None = None,
        merchant_id: str | None = None,
        page: int | None = None,
        size: int | None = None,
        sort: str | None = None):
    """API to get reward batches for an initiative.
        GET /initiatives/{initiativeId}/reward-batches
        parameters:
        status: reward batch status
        assignee_level: assigned operator level (L1, L2, L3)
        month: reward batch month
        merchant_id: merchant id
        page: page number
        size: page size
        sort: sort order
    """
    params = {}

    if status is not None:
        params['status'] = status
    if assignee_level is not None:
        params['assigneeLevel'] = assignee_level
    if month is not None:
        params['month'] = month
    if merchant_id is not None:
        params['merchantId'] = merchant_id
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size
    if sort is not None:
        params['sort'] = sort

    return requests.get(
        f"{secrets.base_path.IO}{settings.IDPAY.domain}"
        f"{settings.IDPAY.endpoints.transactions.merchant}/initiatives"
        f"/{initiative_id}/reward-batches",
        params=params,
        timeout=settings.default_timeout
    )

def post_reward_batch_confirmation_batch(initiative_id: str,
                                        request_body: dict):
    return requests.post(
        f'{secrets.base_path.IDPAY.internal}{settings.IDPAY.endpoints.transactions.path}'
        f'{settings.IDPAY.endpoints.transactions.reward_batches}/{initiative_id}'
        f'/reward-batches/approved',
        json=request_body,
        timeout=settings.default_timeout
    )


def post_generate_report(initiative_id: str,
                         request_body: ReportRequest,
                         merchant_id: str | None = None,
                         access_token: str | None = None):
    params = {}
    headers = {}
    if merchant_id is not None:
        params['merchantId'] = merchant_id
    if access_token is not None:
        headers['Authorization'] = f"Bearer {access_token}"

    return requests.post(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.transactions.merchant}'
        f'/initiative/{initiative_id}/reports',
        headers=headers,
        params=params,
        json=request_body.to_dict(),
        timeout=settings.default_timeout
    )


def get_reports(initiative_id: str,
                report_type: str | None = None,
                page: int | None = None,
                size: int | None = None,
                access_token: str | None = None):
    params = {}
    headers = {}

    if report_type is not None:
        params['reportType'] = report_type
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size
    if access_token is not None:
        headers['Authorization'] = f"Bearer {access_token}"

    return requests.get(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.transactions.merchant}'
        f'/initiative/{initiative_id}/reports',
        headers=headers,
        params=params,
        timeout=settings.default_timeout
    )


def get_report_download(initiative_id: str,
                        report_id: str,
                        access_token: str | None = None):
    headers = {}
    if access_token is not None:
        headers['Authorization'] = f"Bearer {access_token}"

    return requests.get(
        f'{secrets.base_path.IO}{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.transactions.merchant}'
        f'/initiative/{initiative_id}/reports/{report_id}/download',
        headers=headers,
        timeout=settings.default_timeout
    )