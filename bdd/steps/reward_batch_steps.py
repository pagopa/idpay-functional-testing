from behave import then
from behave import when

from api.idpay import get_reward_batch_detail
from api.idpay import post_evaluate_sent_reward_batches
from api.idpay import post_prepare_reward_batch_for_send
from api.idpay import post_send_reward_batch
from util.utility import get_merchant_access_token
from util.utility import retry_reward_batch_eligibility
from util.utility import retry_reward_batch_reassignment


@then('the transaction {trx_name} belongs to a reward batch')
def step_transaction_is_associated_with_reward_batch(context, trx_name):
    merchant_name = context.associated_merchant[trx_name]
    eligibility = retry_reward_batch_eligibility(
        transaction_id=context.transactions[trx_name]['id'],
        merchant_id=context.merchants[merchant_name]['id'],
        access_token=context.transaction_pos_access_tokens[trx_name],
        expected_associated=True
    )
    assert eligibility['transactionId'] == context.transactions[trx_name]['id']
    assert eligibility['initiativeId'] == context.initiative_id
    assert eligibility['merchantId'] == context.merchants[merchant_name]['id']
    assert eligibility['rewardBatchId']


@then('the transaction {trx_name} does not belong to a reward batch')
def step_transaction_is_not_associated_with_reward_batch(context, trx_name):
    merchant_name = context.associated_merchant[trx_name]
    retry_reward_batch_eligibility(
        transaction_id=context.transactions[trx_name]['id'],
        merchant_id=context.merchants[merchant_name]['id'],
        access_token=context.transaction_pos_access_tokens[trx_name],
        expected_associated=False
    )


@when('the reward batch of transaction {trx_name} is prepared and sent')
def step_prepare_and_send_reward_batch(context, trx_name):
    merchant_name = context.associated_merchant[trx_name]
    merchant_id = context.merchants[merchant_name]['id']
    access_token = context.transaction_pos_access_tokens[trx_name]
    eligibility = retry_reward_batch_eligibility(
        transaction_id=context.transactions[trx_name]['id'],
        merchant_id=merchant_id,
        access_token=access_token,
        expected_associated=True
    )
    source_reward_batch_id = eligibility['rewardBatchId']

    source_batch_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=source_reward_batch_id,
        merchant_id=merchant_id
    )
    assert source_batch_response.status_code == 200, (
        f'Reward batch detail failed before preparation: '
        f'{source_batch_response.status_code} {source_batch_response.text}'
    )
    source_batch = source_batch_response.json()
    assert source_batch['status'] == 'CREATED'

    prepare_response = post_prepare_reward_batch_for_send(
        initiative_id=context.initiative_id,
        reward_batch_id=source_reward_batch_id
    )
    assert prepare_response.status_code == 200, (
        f'Reward batch preparation failed: '
        f'{prepare_response.status_code} {prepare_response.text}'
    )
    prepared_batch = prepare_response.json()
    assert prepared_batch['rewardBatchId'] == source_reward_batch_id
    assert prepared_batch['previousMonth'] == source_batch['month']

    send_response = post_send_reward_batch(
        initiative_id=context.initiative_id,
        reward_batch_id=source_reward_batch_id,
        access_token=get_merchant_access_token(merchant_name)
    )
    assert send_response.status_code == 204, (
        f'Reward batch send failed: {send_response.status_code} {send_response.text}'
    )

    sent_batch_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=source_reward_batch_id,
        merchant_id=merchant_id
    )
    assert sent_batch_response.status_code == 200
    sent_batch = sent_batch_response.json()
    assert sent_batch['status'] == 'SENT'
    assert sent_batch['month'] == prepared_batch['referenceMonth']

    if not hasattr(context, 'source_reward_batches'):
        context.source_reward_batches = {}
    context.source_reward_batches[trx_name] = sent_batch


@then('the invoice update of transaction {trx_name} is rejected')
def step_invoice_update_is_rejected(context, trx_name):
    response = context.latest_merchant_invoice_update_bar_code
    assert response.status_code == 403, (
        f'Expected invoice update of transaction {trx_name} to be rejected, '
        f'got {response.status_code} {response.text}'
    )
    assert response.json()['code'] == 'PAYMENT_REWARD_BATCH_ELIGIBILITY_NOT_ALLOWED'


@then('the reward batch of transaction {trx_name} is {batch_status}')
def step_reward_batch_has_status(context, trx_name, batch_status):
    merchant_name = context.associated_merchant[trx_name]
    source_batch = context.source_reward_batches[trx_name]
    response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=source_batch['id'],
        merchant_id=context.merchants[merchant_name]['id'],
    )
    assert response.status_code == 200, (
        f'Reward batch detail failed: {response.status_code} {response.text}'
    )
    assert response.json()['status'] == batch_status


@when('the specific reward batch of transaction {trx_name} is evaluated')
def step_evaluate_specific_sent_reward_batch(context, trx_name):
    merchant_name = context.associated_merchant[trx_name]
    merchant_id = context.merchants[merchant_name]['id']
    source_batch = context.source_reward_batches[trx_name]
    response = post_evaluate_sent_reward_batches(
        initiative_id=context.initiative_id,
        reward_batch_ids=[source_batch['id']]
    )
    assert response.status_code == 200, (
        f'SENT reward batch evaluation failed: {response.status_code} {response.text}'
    )

    source_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=source_batch['id'],
        merchant_id=merchant_id
    )
    assert source_response.status_code == 200
    assert source_response.json()['status'] == 'EVALUATING'


@then('the transaction {trx_name} belongs to a different current-month reward batch as {batch_transaction_status}')
def step_transaction_is_reassigned_after_invoice_update(context, trx_name, batch_transaction_status):
    merchant_name = context.associated_merchant[trx_name]
    merchant_id = context.merchants[merchant_name]['id']
    source_batch = context.source_reward_batches[trx_name]
    eligibility = retry_reward_batch_reassignment(
        transaction_id=context.transactions[trx_name]['id'],
        merchant_id=merchant_id,
        access_token=context.transaction_pos_access_tokens[trx_name],
        original_reward_batch_id=source_batch['id'],
        expected_batch_transaction_status=batch_transaction_status
    )

    destination_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=eligibility['rewardBatchId'],
        merchant_id=merchant_id
    )
    assert destination_response.status_code == 200, (
        f'Destination reward batch detail failed: '
        f'{destination_response.status_code} {destination_response.text}'
    )
    destination_batch = destination_response.json()
    assert destination_batch['id'] != source_batch['id']
    assert destination_batch['initiativeId'] == context.initiative_id
    assert destination_batch['merchantId'] == merchant_id
    assert destination_batch['posType'] == source_batch['posType']
    assert destination_batch['status'] == 'CREATED'
    assert destination_batch['month'] in context.invoice_update_months[trx_name]

    source_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=source_batch['id'],
        merchant_id=merchant_id
    )
    assert source_response.status_code == 200
    assert source_response.json()['status'] == 'EVALUATING'
