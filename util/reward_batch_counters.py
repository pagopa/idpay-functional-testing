'''Pure reward-batch counter formulas shared by unit and BDD tests.'''

ELABORATED_STATUSES = {'SUSPENDED', 'APPROVED', 'REJECTED'}
APPROVED_AMOUNT_STATUSES = {'TO_CHECK', 'CONSULTABLE', 'APPROVED'}
LIVE_SUSPENDED_BATCH_STATUSES = {'CREATED', 'SENT', 'EVALUATING'}


def transaction_reward_amount(transaction: dict) -> int:
    '''Return the materialized reward amount exposed by a transaction API.'''
    for field in ('rewardAmountCents', 'accruedRewardCents'):
        value = transaction.get(field)
        if value is not None:
            return int(value)
    raise AssertionError(
        'Transaction does not expose rewardAmountCents or accruedRewardCents: '
        f'{transaction}'
    )


def transaction_batch_status(transaction: dict) -> str | None:
    value = transaction.get('rewardBatchTrxStatus')
    return value.upper() if isinstance(value, str) else value


def derive_live_counters(transactions: list[dict]) -> dict[str, int]:
    '''Calculate every counter whose value is always derived from current rows.'''
    rows = [
        (transaction_batch_status(transaction), transaction_reward_amount(transaction))
        for transaction in transactions
    ]
    return {
        'numberOfTransactions': len(rows),
        'numberOfTransactionsElaborated': sum(
            status in ELABORATED_STATUSES for status, _ in rows
        ),
        'numberOfTransactionsSuspended': sum(
            status == 'SUSPENDED' for status, _ in rows
        ),
        'numberOfTransactionsRejected': sum(
            status == 'REJECTED' for status, _ in rows
        ),
        'currentAmountCents': sum(amount for _, amount in rows),
        'excludedAmountCents': sum(
            amount for status, amount in rows if status == 'REJECTED'
        ),
    }


def derive_state_dependent_live_counters(
    batch_status: str,
    transactions: list[dict],
) -> dict[str, int]:
    '''Calculate exposed amounts that are live for the supplied batch state.'''
    normalized_batch_status = batch_status.upper()
    rows = [
        (transaction_batch_status(transaction), transaction_reward_amount(transaction))
        for transaction in transactions
    ]
    counters = {
        'approvedAmountCents': 0
        if normalized_batch_status in {'CREATED', 'SENT'}
        else sum(
            amount
            for status, amount in rows
            if status in APPROVED_AMOUNT_STATUSES
        )
    }
    if normalized_batch_status == 'CREATED':
        counters['initialAmountCents'] = sum(amount for _, amount in rows)
    if normalized_batch_status in LIVE_SUSPENDED_BATCH_STATUSES:
        counters['suspendedAmountCents'] = sum(
            amount for status, amount in rows if status == 'SUSPENDED'
        )
    return counters


def derive_visible_live_counters(
    batch_status: str,
    transactions: list[dict],
) -> dict[str, int]:
    '''Return all counters that must agree with current membership in this state.'''
    return {
        **derive_live_counters(transactions),
        **derive_state_dependent_live_counters(batch_status, transactions),
    }
