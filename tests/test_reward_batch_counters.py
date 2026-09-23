import pytest

from util.reward_batch_counters import derive_visible_live_counters


def transaction(status, amount):
    return {
        'rewardBatchTrxStatus': status,
        'rewardAmountCents': amount,
    }


@pytest.mark.parametrize(
    ('batch_status', 'expected_approved', 'expected_suspended'),
    [
        ('CREATED', 0, 200),
        ('SENT', 0, 200),
        ('EVALUATING', 400, 200),
    ],
)
def test_live_amounts_follow_batch_status(
    batch_status,
    expected_approved,
    expected_suspended,
):
    counters = derive_visible_live_counters(
        batch_status,
        [
            transaction('CONSULTABLE', 100),
            transaction('TO_CHECK', 100),
            transaction('SUSPENDED', 200),
            transaction('APPROVED', 200),
            transaction('REJECTED', 300),
        ],
    )

    assert counters['numberOfTransactions'] == 5
    assert counters['numberOfTransactionsElaborated'] == 3
    assert counters['numberOfTransactionsSuspended'] == 1
    assert counters['numberOfTransactionsRejected'] == 1
    assert counters['currentAmountCents'] == 900
    assert counters['excludedAmountCents'] == 300
    assert counters['approvedAmountCents'] == expected_approved
    assert counters['suspendedAmountCents'] == expected_suspended


def test_created_initial_amount_is_live():
    counters = derive_visible_live_counters(
        'CREATED',
        [transaction('CONSULTABLE', 100), transaction('SUSPENDED', 200)],
    )

    assert counters['initialAmountCents'] == 300


def test_initial_amount_is_not_derived_after_send():
    counters = derive_visible_live_counters(
        'SENT',
        [transaction('CONSULTABLE', 100)],
    )

    assert 'initialAmountCents' not in counters


def test_suspended_amount_is_not_derived_after_approving():
    counters = derive_visible_live_counters(
        'APPROVING',
        [transaction('SUSPENDED', 200)],
    )

    assert 'suspendedAmountCents' not in counters


def test_rejected_counters_remain_live_after_approving():
    counters = derive_visible_live_counters(
        'APPROVED',
        [transaction('REJECTED', 300), transaction('APPROVED', 200)],
    )

    assert counters['numberOfTransactionsRejected'] == 1
    assert counters['excludedAmountCents'] == 300


def test_reversal_is_equivalent_to_removing_the_transaction_from_membership():
    before = derive_visible_live_counters(
        'EVALUATING',
        [transaction('REJECTED', 300), transaction('APPROVED', 200)],
    )
    after = derive_visible_live_counters(
        'EVALUATING',
        [transaction('APPROVED', 200)],
    )

    assert after['numberOfTransactions'] == before['numberOfTransactions'] - 1
    assert after['numberOfTransactionsElaborated'] == 1
    assert after['numberOfTransactionsRejected'] == 0
    assert after['currentAmountCents'] == 200
    assert after['excludedAmountCents'] == 0


@pytest.mark.parametrize('transaction_status', ['CONSULTABLE', 'SUSPENDED'])
def test_postpone_moves_the_same_live_contribution_between_created_batches(
    transaction_status,
):
    moved_transaction = transaction(transaction_status, 200)
    source_before = derive_visible_live_counters('CREATED', [moved_transaction])
    source_after = derive_visible_live_counters('CREATED', [])
    destination_before = derive_visible_live_counters('CREATED', [])
    destination_after = derive_visible_live_counters(
        'CREATED',
        [moved_transaction],
    )

    assert source_after['numberOfTransactions'] == 0
    assert source_after['currentAmountCents'] == 0
    assert source_after['initialAmountCents'] == 0
    assert destination_after == source_before
    assert destination_before == source_after
