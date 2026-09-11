from behave import given
from behave import then
from behave import when

from api.idpay import get_merchant_processed_transactions
from api.idpay import get_reward_batch_detail
from api.idpay import post_evaluate_sent_reward_batches
from api.idpay import post_prepare_reward_batch_for_send
from api.idpay import post_send_reward_batch
from bdd.steps.bar_code_steps import get_point_of_sale_access_token
from bdd.steps.bar_code_steps import reverse_bar_code_transaction
from api.transaction import post_approve_reward_batch, post_reward_batch_confirmation_batch, \
    get_approved_reward_batch_download
from util.transaction_utilities import assert_transactions_share_same_reward_batch
from util.transaction_utilities import assert_transaction_in_processed_reward_batch
from util.transaction_utilities import get_institution_selfcare_token
from util.transaction_utilities import parse_transaction_names
from util.transaction_utilities import perform_reward_batch_transaction_action
from util.transaction_utilities import request_reward_batch_validation
from util.transaction_utilities import validate_reward_batch_as_operator
from util.utility import get_merchant_access_token
from util.utility import retry_reward_batch_eligibility
from util.utility import retry_reward_batch_reassignment


@then('the transaction {trx_name} belongs to a reward batch')
def step_transaction_is_associated_with_reward_batch(context, trx_name):
    reward_batch_id = _get_associated_reward_batch_id(context, trx_name)
    if not hasattr(context, 'reward_batch_ids'):
        context.reward_batch_ids = {}
    context.reward_batch_ids[trx_name] = reward_batch_id


@then('the transaction {trx_name} belongs to the reward batch named {batch_name}')
def step_transaction_is_associated_with_named_reward_batch(context, trx_name, batch_name):
    step_transaction_is_associated_with_reward_batch(context, trx_name)
    if not hasattr(context, 'reward_batch_aliases'):
        context.reward_batch_aliases = {}
    context.reward_batch_aliases[batch_name] = trx_name


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
    reward_batch_id = _get_associated_reward_batch_id(context, trx_name)
    _prepare_and_send_reward_batch(
        context=context,
        trx_name=trx_name,
        reward_batch_id=reward_batch_id
    )


@when('the merchant {merchant_name} prepares and sends the reward batch named {batch_name}')
def step_prepare_and_send_named_reward_batch(context, merchant_name, batch_name):
    _prepare_and_send_empty_reward_batch(
        context=context,
        merchant_name=merchant_name,
        trx_name=_stored_reward_batch_transaction(context, batch_name)
    )


def _prepare_and_send_empty_reward_batch(context, merchant_name, trx_name):
    assert context.associated_merchant[trx_name] == merchant_name, (
        f'Transaction {trx_name} is not associated with merchant {merchant_name}'
    )
    _prepare_and_send_reward_batch(
        context=context,
        trx_name=trx_name,
        reward_batch_id=_stored_reward_batch_id(context, trx_name),
        expected_number_of_transactions=0
    )


def _reverse_reward_batch_transactions(
        context, point_of_sale_name, merchant_name, trx_name
):
    assert context.associated_merchant[trx_name] == merchant_name, (
        f'Transaction {trx_name} is not associated with merchant {merchant_name}'
    )
    reward_batch_id = _stored_reward_batch_id(context, trx_name)
    merchant_id = context.merchants[merchant_name]['id']
    batch_transactions = _get_reward_batch_transactions(
        initiative_id=context.initiative_id,
        merchant_id=merchant_id,
        reward_batch_id=reward_batch_id,
        access_token=get_merchant_access_token(merchant_name)
    )

    access_token = get_point_of_sale_access_token(
        merchant_name=merchant_name,
        point_of_sale_name=point_of_sale_name
    )
    for transaction in batch_transactions:
        assert transaction['status'] == 'INVOICED', (
            f'Transaction {transaction["trxId"]} in reward batch {reward_batch_id} '
            f'has status {transaction["status"]} and cannot be reversed'
        )
        reverse_bar_code_transaction(
            initiative_id=context.initiative_id,
            transaction_id=transaction['trxId'],
            access_token=access_token
        )
        retry_reward_batch_eligibility(
            transaction_id=transaction['trxId'],
            merchant_id=merchant_id,
            access_token=access_token,
            expected_associated=False
        )


@when(
    'the point of sale {point_of_sale_name} of merchant {merchant_name} reverses all transactions '
    'in the reward batch named {batch_name}'
)
def step_reverse_named_reward_batch_transactions(
        context, point_of_sale_name, merchant_name, batch_name
):
    _reverse_reward_batch_transactions(
        context=context,
        point_of_sale_name=point_of_sale_name,
        merchant_name=merchant_name,
        trx_name=_stored_reward_batch_transaction(context, batch_name)
    )


def _reward_batch_has_transaction_count(context, trx_name, expected_number_of_transactions):
    response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=_stored_reward_batch_id(context, trx_name),
        merchant_id=context.merchants[context.associated_merchant[trx_name]]['id']
    )
    assert response.status_code == 200, (
        f'Reward batch detail failed while checking transaction count: '
        f'{response.status_code} {response.text}'
    )
    actual_number_of_transactions = response.json()['numberOfTransactions']
    assert actual_number_of_transactions == int(expected_number_of_transactions), (
        f'Expected reward batch to contain {expected_number_of_transactions} transactions, '
        f'got {actual_number_of_transactions}'
    )


@then(
    'the reward batch named {batch_name} contains {expected_number_of_transactions} transactions'
)
def step_named_reward_batch_has_transaction_count(
        context, batch_name, expected_number_of_transactions
):
    _reward_batch_has_transaction_count(
        context=context,
        trx_name=_stored_reward_batch_transaction(context, batch_name),
        expected_number_of_transactions=expected_number_of_transactions
    )


def _get_associated_reward_batch_id(context, trx_name):
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
    return eligibility['rewardBatchId']


def _stored_reward_batch_id(context, trx_name):
    assert hasattr(context, 'reward_batch_ids') and trx_name in context.reward_batch_ids, (
        f'Reward batch ID for transaction {trx_name} was not captured before reversal'
    )
    return context.reward_batch_ids[trx_name]


def _stored_reward_batch_transaction(context, batch_name):
    assert hasattr(context, 'reward_batch_aliases') and batch_name in context.reward_batch_aliases, (
        f'Reward batch alias {batch_name} was not captured before use'
    )
    return context.reward_batch_aliases[batch_name]


def _get_reward_batch_transactions(initiative_id, merchant_id, reward_batch_id, access_token):
    transactions = []
    page = 0
    while True:
        response = get_merchant_processed_transactions(
            initiative_id=initiative_id,
            merchant_id=merchant_id,
            access_token=access_token,
            page=page,
            size=100,
            reward_batch_id=reward_batch_id
        )
        assert response.status_code == 200, (
            f'Reward batch transactions request failed: '
            f'{response.status_code} {response.text}'
        )
        page_data = response.json()
        transactions.extend(page_data['content'])
        if page + 1 >= page_data['totalPages']:
            return transactions
        page += 1


def _prepare_and_send_reward_batch(
        context, trx_name, reward_batch_id, expected_number_of_transactions=None
):
    merchant_name = context.associated_merchant[trx_name]
    merchant_id = context.merchants[merchant_name]['id']

    source_batch_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        merchant_id=merchant_id
    )
    assert source_batch_response.status_code == 200, (
        f'Reward batch detail failed before preparation: '
        f'{source_batch_response.status_code} {source_batch_response.text}'
    )
    source_batch = source_batch_response.json()
    assert source_batch['status'] == 'CREATED'
    if expected_number_of_transactions is not None:
        assert source_batch['numberOfTransactions'] == expected_number_of_transactions, (
            f'Expected reward batch {reward_batch_id} to contain '
            f'{expected_number_of_transactions} transactions before sending, '
            f'got {source_batch["numberOfTransactions"]}'
        )

    prepare_response = post_prepare_reward_batch_for_send(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id
    )
    assert prepare_response.status_code == 200, (
        f'Reward batch preparation failed: '
        f'{prepare_response.status_code} {prepare_response.text}'
    )
    prepared_batch = prepare_response.json()
    assert prepared_batch['rewardBatchId'] == reward_batch_id
    assert prepared_batch['previousMonth'] == source_batch['month']

    send_response = post_send_reward_batch(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=get_merchant_access_token(merchant_name)
    )
    defer_send_outcome_assertion = expected_number_of_transactions == 0
    if not defer_send_outcome_assertion:
        assert send_response.status_code == 204, (
            f'Reward batch send failed: {send_response.status_code} {send_response.text}'
        )
    if not hasattr(context, 'reward_batch_send_responses'):
        context.reward_batch_send_responses = {}
    context.reward_batch_send_responses[reward_batch_id] = send_response

    sent_batch_response = get_reward_batch_detail(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        merchant_id=merchant_id
    )
    assert sent_batch_response.status_code == 200
    sent_batch = sent_batch_response.json()
    if not defer_send_outcome_assertion:
        assert sent_batch['status'] == 'SENT'
    assert sent_batch['month'] == prepared_batch['referenceMonth']
    if expected_number_of_transactions is not None:
        assert sent_batch['numberOfTransactions'] == expected_number_of_transactions, (
            f'Expected sent reward batch {reward_batch_id} to contain '
            f'{expected_number_of_transactions} transactions, '
            f'got {sent_batch["numberOfTransactions"]}'
        )

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

@when('the reward batch of transaction {trx_name} is {batch_status:w}')
@then('the reward batch of transaction {trx_name} is {batch_status:w}')
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
    actual_status = response.json()['status']
    send_response = getattr(context, 'reward_batch_send_responses', {}).get(source_batch['id'])
    send_response_details = ''
    if send_response is not None:
        send_response_details = (
            f' Send response: {send_response.status_code} {send_response.text}'
        )
    assert actual_status == batch_status, (
        f'Expected reward batch {source_batch["id"]} to be {batch_status}, '
        f'got {actual_status}.{send_response_details}'
    )
    return response.json()


@then('the reward batch named {batch_name} is {batch_status}')
def step_named_reward_batch_has_status(context, batch_name, batch_status):
    step_reward_batch_has_status(
        context=context,
        trx_name=_stored_reward_batch_transaction(context, batch_name),
        batch_status=batch_status
    )


@given('the reward batch of transaction {trx_name} is {status} and assigned to {assigneeLevel}')
@when('the reward batch of transaction {trx_name} is {status} and assigned to {assigneeLevel}')
@then('the reward batch of transaction {trx_name} is {status} and assigned to {assigneeLevel}')
def step_reward_batch_has_status_and_assigned_level(context, trx_name, status, assigneeLevel):
    status = status.upper()
    response = step_reward_batch_has_status(context, trx_name, status)
    assert response['assigneeLevel'] == assigneeLevel.upper(), (f"status and level {response['status']} {response['assigneeLevel']} ")

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


@given('the transaction {trx_name} is prepared, sent and evaluated in reward batch status {batch_status}')
def step_full_performing_trx_to_reward_batch(context, trx_name, batch_status):
    step_transaction_is_associated_with_reward_batch(context, trx_name)
    step_prepare_and_send_reward_batch(context, trx_name)
    step_reward_batch_has_status(context, trx_name, 'SENT')
    step_evaluate_specific_sent_reward_batch(context, trx_name)
    step_reward_batch_has_status(context, trx_name, batch_status)


def _prepare_send_evaluate_same_reward_batch(context, trx_names: list[str], batch_status: str):
    merchant_names = [context.associated_merchant[trx_name] for trx_name in trx_names]
    assert len(set(merchant_names)) == 1, (
        f'Transactions are on different merchants: {merchant_names}'
    )

    for trx_name in trx_names:
        step_transaction_is_associated_with_reward_batch(context, trx_name)

    merchant_id = context.merchants[merchant_names[0]]['id']
    assert_transactions_share_same_reward_batch(
        trx_names=trx_names,
        transaction_ids_by_name={
            trx_name: context.transactions[trx_name]['id']
            for trx_name in trx_names
        },
        access_tokens_by_name={
            trx_name: context.transaction_pos_access_tokens[trx_name]
            for trx_name in trx_names
        },
        merchant_id=merchant_id,
    )

    first_trx_name = trx_names[0]

    step_prepare_and_send_reward_batch(context, first_trx_name)
    if not hasattr(context, 'source_reward_batches'):
        context.source_reward_batches = {}
    for trx_name in trx_names[1:]:
        context.source_reward_batches[trx_name] = context.source_reward_batches[first_trx_name]

    for trx_name in trx_names:
        step_reward_batch_has_status(context, trx_name, 'SENT')
    step_evaluate_specific_sent_reward_batch(context, first_trx_name)
    for trx_name in trx_names:
        step_reward_batch_has_status(context, trx_name, batch_status)


@given('the transactions {trx_names} are prepared, sent and evaluated in the same reward batch status {batch_status}')
def step_full_performing_n_trx_to_same_reward_batch(context, trx_names, batch_status):
    parsed_trx_names = parse_transaction_names(trx_names)
    _prepare_send_evaluate_same_reward_batch(context, parsed_trx_names, batch_status)


@given('An operator with {role} role select transaction {trx_name} from reward batch list and {transaction_action} it')
@when('An operator with {role} role select transaction {trx_name} from reward batch list and {transaction_action} it')
@when('An operator with {role} role select transaction {trx_name} from reward batch list and tries to {transaction_action} it')
def step_operator_select_and_do_an_action_on_reward_batch_trx(context, role, trx_name, transaction_action):
    merchant_name = context.associated_merchant[trx_name]
    transaction_id = context.transactions[trx_name]['id']
    reward_batch_id = context.source_reward_batches[trx_name]['id']
    institution_selfcare_token = get_institution_selfcare_token(role)

    assert_transaction_in_processed_reward_batch(
        merchant_id=context.merchants[merchant_name]['id'],
        initiative_id=context.initiative_id,
        access_token=institution_selfcare_token,
        reward_batch_id=reward_batch_id,
        transaction_id=transaction_id,
    )
    action_response = perform_reward_batch_transaction_action(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=institution_selfcare_token,
        transaction_id=transaction_id,
        transaction_action=transaction_action,
    )
    context.latest_reward_batch_transaction_action_response = action_response

@given('An operator with {role} role validating the reward batch containing transaction {trx_name}')
@when('An operator with {role} role validating the reward batch containing transaction {trx_name}')
def step_operator_validate_reward_batch(context, role, trx_name):
    reward_batch_id = context.source_reward_batches[trx_name]['id']
    institution_selfcare_token = get_institution_selfcare_token(role)

    validate_reward_batch_as_operator(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=institution_selfcare_token,
    )

@when('An operator with {role} role tries to approve the reward batch containing transaction {trx_name}')
def step_operator_approve_reward_batch(context, role, trx_name):
    reward_batch_id = context.source_reward_batches[trx_name]['id']
    institution_selfcare_token = get_institution_selfcare_token(role)

    approve_reward_batch = post_approve_reward_batch(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=institution_selfcare_token,
    )

    assert approve_reward_batch.status_code == 200, (
        f"Reward batch approval failed: "
        f"{approve_reward_batch.status_code} {approve_reward_batch.text}"
    )

    reward_batch_confirmation_batch = post_reward_batch_confirmation_batch(
        initiative_id=context.initiative_id,
        request_body={
            "rewardBatchId": reward_batch_id
        }
    )

    assert reward_batch_confirmation_batch.status_code == 200, (
        f"Reward batch confirmation failed: "
        f"{reward_batch_confirmation_batch.status_code} {reward_batch_confirmation_batch.text}"
    )


@when('An operator with {role} role downloads the approved reward batch report of transaction {trx_name} after {wait_seconds} seconds')
def step_operator_downloads_approved_reward_batch_report(context, role, trx_name, wait_seconds):
    reward_batch_id = context.source_reward_batches[trx_name]['id']
    merchant_name = context.associated_merchant[trx_name]
    institution_selfcare_token = get_institution_selfcare_token(role)

    download_response = get_approved_reward_batch_download(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=institution_selfcare_token,
        wait_seconds=float(wait_seconds),
    )
    assert download_response.status_code == 200, (
        f"Approved reward batch download failed: "
        f"{download_response.status_code} {download_response.text}"
    )
    assert download_response.content, 'Approved reward batch download returned empty content'
    context.latest_approved_reward_batch_download = download_response
    context.latest_approved_reward_batch_download_merchant = merchant_name


@then('the approved reward batch report of transaction {trx_name} is downloaded')
def step_approved_reward_batch_report_is_downloaded(context, trx_name):
    response = context.latest_approved_reward_batch_download
    assert response.status_code == 200, (
        f"Approved reward batch report of transaction {trx_name} was not downloaded: "
        f"{response.status_code} {response.text}"
    )
    assert response.content

@when('An operator with {role} role fails when tries to validate the reward batch containing transaction {trx_name} for {reason}')
def step_operator_validation_reward_batch_fails(context, role, trx_name, reason):
    reward_batch_id = context.source_reward_batches[trx_name]['id']
    institution_selfcare_token = get_institution_selfcare_token(role)

    validate_reward_batch = request_reward_batch_validation(
        initiative_id=context.initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=institution_selfcare_token,
    )

    if reason == 'UNSATISFIED MINIMUM ELABORATION PERCENT':
        assert validate_reward_batch.status_code == 400
        assert validate_reward_batch.json()['code'] == 'BATCH_NOT_ELABORATED_15_PERCENT'
