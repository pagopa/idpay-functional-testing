import time

from behave import given
from behave import then
from behave import when

from api.idpay import get_reward_batch_detail
from util.reward_batch_counters import derive_visible_live_counters
from util.reward_batch_counters import transaction_batch_status
from util.reward_batch_counters import transaction_reward_amount
from util.transaction_utilities import get_reward_batch_transactions
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
    tracked_batches = getattr(context, 'tracked_counter_batches', {})
    if batch_reference in tracked_batches:
        tracked = tracked_batches[batch_reference]
        return _batch_observation_by_id(
            context=context,
            merchant_name=tracked['merchant_name'],
            reward_batch_id=tracked['id'],
        )

    transaction_name = _transaction_for_batch_reference(context, batch_reference)
    merchant_name = context.associated_merchant[transaction_name]
    reward_batch_id = _batch_id(context, transaction_name)
    return _batch_observation_by_id(context, merchant_name, reward_batch_id)


def _batch_observation_by_id(context, merchant_name, reward_batch_id):
    merchant_id = context.merchants[merchant_name]['id']

    detail_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        merchant_id=merchant_id,
    )
    assert detail_response.status_code == 200, (
        'Reward batch detail failed: '
        f'{detail_response.status_code} {detail_response.text}'
    )

    transactions = get_reward_batch_transactions(
        initiative_id=context.initiative_id,
        merchant_id=merchant_id,
        reward_batch_id=reward_batch_id,
        access_token=get_merchant_access_token(
            initiative_name=context.initiative_name, merchant_name=merchant_name
        ),
    )

    return detail_response.json(), transactions


def _track_observed_batch(context, batch_reference, batch):
    transaction_name = _transaction_for_batch_reference(context, batch_reference)
    merchant_name = context.associated_merchant[transaction_name]
    if not hasattr(context, 'tracked_counter_batches'):
        context.tracked_counter_batches = {}
    context.tracked_counter_batches[batch_reference] = {
        'id': batch['id'],
        'merchant_name': merchant_name,
    }


def _counter_differences(actual, expected):
    return {
        field: {'expected': value, 'actual': actual.get(field)}
        for field, value in expected.items()
        if actual.get(field) != value
    }


def _wait_for_live_counter_consistency(observe_batch):
    for attempt in range(20):
        batch, transactions = observe_batch()
        expected = derive_visible_live_counters(batch['status'], transactions)
        differences = _counter_differences(batch, expected)
        if not differences:
            return batch, transactions
        if attempt < 19:
            time.sleep(0.5)

    raise AssertionError(
        f"Reward batch {batch['id']} counters do not match current transactions. "
        f"Differences: {differences}"
    )


@given(
    'the counters of reward batch {batch_reference} are captured as {baseline_name}'
)
@when(
    'the counters of reward batch {batch_reference} are captured as {baseline_name}'
)
@then(
    'the counters of reward batch {batch_reference} are captured as {baseline_name}'
)
def step_capture_reward_batch_counters(context, batch_reference, baseline_name):
    batch, transactions = _wait_for_live_counter_consistency(
        lambda: _batch_observation(context, batch_reference)
    )
    if batch["status"] == "SENT":
        expected_initial_amount = sum(
            transaction_reward_amount(transaction) for transaction in transactions
        )
        assert batch["initialAmountCents"] == expected_initial_amount, (
            f"Expected sent initialAmountCents {expected_initial_amount}, "
            f"got {batch['initialAmountCents']}"
        )
    _track_observed_batch(context, batch_reference, batch)
    if not hasattr(context, 'reward_batch_counter_baselines'):
        context.reward_batch_counter_baselines = {}
    context.reward_batch_counter_baselines[baseline_name] = {
        'batch': batch,
        'transactions': transactions,
    }


@then("the transaction {transaction_name} is REJECTED in its reward batch")
def step_reward_batch_transaction_is_rejected(context, transaction_name):
    transaction_id = context.transactions[transaction_name]["id"]
    actual_status = None
    for attempt in range(20):
        _, transactions = _batch_observation(context, transaction_name)
        transaction = next(
            (
                row for row in transactions
                if row["trxId"].strip() == transaction_id.strip()
            ),
            None,
        )
        actual_status = (
            transaction_batch_status(transaction) if transaction is not None else None
        )
        if actual_status == "REJECTED":
            return
        if attempt < 19:
            time.sleep(0.5)
    raise AssertionError(
        f"Expected transaction {transaction_name} to be REJECTED in its reward batch, "
        f"got {actual_status}"
    )


@then(
    'the live counters of reward batch {batch_reference} match its current transactions'
)
def step_live_reward_batch_counters_match(context, batch_reference):
    _wait_for_live_counter_consistency(
        lambda: _batch_observation(context, batch_reference)
    )


@then(
    'the destination reward batch of transaction {transaction_name} has live counters '
    'matching its current transactions'
)
def step_destination_reward_batch_counters_match(context, transaction_name):
    destination = context.destination_reward_batches[transaction_name]
    merchant_name = context.associated_merchant[transaction_name]
    _wait_for_live_counter_consistency(
        lambda: _batch_observation_by_id(
            context,
            merchant_name,
            destination['id'],
        )
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


@then('reward batch {batch_reference} has zero initial amount')
def step_reward_batch_has_zero_initial_amount(context, batch_reference):
    batch, _ = _batch_observation(context, batch_reference)
    assert batch['initialAmountCents'] == 0, (
        f"Expected initialAmountCents 0, got {batch['initialAmountCents']}"
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
