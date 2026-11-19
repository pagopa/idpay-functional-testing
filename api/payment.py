import datetime

import requests

from conf.configuration import secrets
from conf.configuration import settings


def patch_transaction_end_date(
        transaction_id: str,
        initiative_id: str,
        user_id: str,
        new_end_date: datetime.datetime):
    """Update a transaction end date using an offset-aware datetime."""
    if new_end_date.utcoffset() is None:
        raise ValueError('new_end_date must include a timezone offset')

    payment = settings.IDPAY.endpoints.payment
    return requests.patch(
        f'{secrets.base_path.IDPAY.internal.rstrip("/")}{payment.internal_path}'
        f'{payment.transaction_end_date_test_support.format(transaction_id=transaction_id)}',
        params={
            'initiativeId': initiative_id,
            'userId': user_id,
            'newEndDate': new_end_date.isoformat(),
        },
        timeout=settings.default_timeout,
    )


def post_update_expired_transactions_status(initiative_id: str):
    """Process expired transactions and return the raw response with counters."""
    payment = settings.IDPAY.endpoints.payment
    return requests.post(
        f'{secrets.base_path.IDPAY.internal.rstrip("/")}{payment.internal_path}'
        f'{payment.expired_transactions_update_status.format(initiative_id=initiative_id)}',
        timeout=settings.default_timeout,
    )
