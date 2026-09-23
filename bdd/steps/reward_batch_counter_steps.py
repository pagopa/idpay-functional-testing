import time

from behave import given
from behave import then

from api.idpay import get_merchant_processed_transactions
from api.idpay import get_reward_batch_detail
from util.reward_batch_counters import derive_visible_live_counters
from util.utility import get_merchant_access_token


def _transaction_for_batch_reference(context, batch_reference):
    aliases = getattr(context, 'reward_batch_aliases', {})
    return aliases.get(batch_reference, batch_reference)


def _batch_id(context, transaction_name):
    captured_ids = getattr(context, 'reward_batch_ids', {})
    if transaction_name in captured_ids:
        return captured_ids[transaction_name]
    source_batches = getattr(context, 'source_reward_batches', {})
    if transaction_name in source_batches:
        return source_batches[transaction_name]['id']
    raise AssertionError(
        f'Reward batch for transaction {transaction_name} was not captured'
    )


def _batch_observation(context, batch_reference):
    transaction_name = _transaction_for_batch_reference(context, batch_reference)
    merchant_name = context.associated_merchant[transaction_name]
    merchant_id = context.merchants[merchant_name]['id']
    reward_batch_id = _batch_id(context, transaction_name)

    detail_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        merchant_id=merchant_id,
    )
    assert detail_response.status_code == 200, (
        'Reward batch detail failed: '
        f'{detail_response.status_code} {detail_response.text}'
    )

    transactions = []
    page = 0
    while True:
        transactions_response = get_merchant_processed_transactions(
            initiative_id=context.initiative_id,
            merchant_id=merchant_id,
            access_token=get_merchant_access_token(merchant_name),
            page=page,
            size=100,
            reward_batch_id=reward_batch_id,
        )
        assert transactions_response.status_code == 200, (
            'Reward batch transactions request failed: '
            f'{transactions_response.status_code} {transactions_response.text}'
        )
        page_data = transactions_response.json()
        transactions.extend(page_data['content'])
        if page + 1 >= page_data['totalPages']:
            break
        page += 1

    return detail_response.json(), transactions


def _counter_differences(actual, expected):
    return {
        field: {'expected': value, 'actual': actual.get(field)}
        for field, value in expected.items()
        if actual.get(field) != value
    }


@given(
    'the counters of reward batch {batch_reference} are captured as {baseline_name}'
)
@then(
    'the counters of reward batch {batch_reference} are captured as {baseline_name}'
)
def step_capture_reward_batch_counters(context, batch_reference, baseline_name):
    batch, transactions = _batch_observation(context, batch_reference)
    if not hasattr(context, 'reward_batch_counter_baselines'):
        context.reward_batch_counter_baselines = {}
    context.reward_batch_counter_baselines[baseline_name] = {
        'batch': batch,
        'transactions': transactions,
    }


@then(
    'the live counters of reward batch {batch_reference} match its current transactions'
)
def step_live_reward_batch_counters_match(context, batch_reference):
    differences = None
    batch = None
    transactions = None
    for attempt in range(20):
        batch, transactions = _batch_observation(context, batch_reference)
        expected = derive_visible_live_counters(batch['status'], transactions)
        differences = _counter_differences(batch, expected)
        if not differences:
            return
        if attempt < 19:
            time.sleep(0.5)

    raise AssertionError(
        f"Reward batch {batch['id']} counters do not match current transactions. "
        f'Differences: {differences}. Transactions: {transactions}'
    )


@then(
    'reward batch {batch_reference} keeps the initial amount captured as {baseline_name}'
)
def step_reward_batch_keeps_initial_snapshot(context, batch_reference, baseline_name):
    batch, _ = _batch_observation(context, batch_reference)
    baseline = context.reward_batch_counter_baselines[baseline_name]['batch']
    assert batch['initialAmountCents'] == baseline['initialAmountCents'], (
        f"Expected initialAmountCents {baseline['initialAmountCents']}, "
        f"got {batch['initialAmountCents']}"
    )


@then(
    'reward batch {batch_reference} keeps the suspended amount captured as {baseline_name}'
)
def step_reward_batch_keeps_suspended_snapshot(
    context,
    batch_reference,
    baseline_name,
):
    batch, _ = _batch_observation(context, batch_reference)
    baseline = context.reward_batch_counter_baselines[baseline_name]['batch']
    assert batch['suspendedAmountCents'] == baseline['suspendedAmountCents'], (
        f"Expected suspendedAmountCents {baseline['suspendedAmountCents']}, "
        f"got {batch['suspendedAmountCents']}"
    )
