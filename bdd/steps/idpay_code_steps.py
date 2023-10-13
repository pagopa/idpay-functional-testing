import binascii
import codecs
import random
from base64 import b64encode
from hashlib import sha256

from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Util.Padding import pad
from behave import given
from behave import then
from behave import when
from psec import tools

from api.idpay import get_idpay_code_status
from api.idpay import get_payment_instruments
from api.idpay import post_idpay_code_generate
from api.idpay import put_code_instrument
from api.idpay import put_minint_associate_user_and_payment
from api.idpay import remove_payment_instrument
from api.idpay import timeline
from api.mil import post_merchant_create_transaction_mil
from api.mil import put_merchant_authorize_transaction_mil
from api.mil import put_merchant_pre_authorize_transaction_mil
from bdd.steps.discount_transaction_steps import step_given_amount_cents
from conf.configuration import settings
from conf.configuration import secrets
from util.utility import get_io_token
from util.utility import check_unprocessed_transactions
from util.utility import tokenize_fc
from util.utility import retry_payment_instrument
from util.utility import retry_timeline

timeline_operations = settings.IDPAY.endpoints.timeline.operations
instrument_types = settings.IDPAY.endpoints.wallet.instrument_type

IV = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
KEY = secrets.encrypt_key_test
PEM_KEY = secrets.public_encrypt_key


@given('the citizen {citizen_name} generates the IDPay Code')
@when('the citizen {citizen_name} generates the IDPay Code')
def step_idpay_code_generate(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io)
    assert res.status_code == 200

    context.idpay_code[citizen_name] = res.json()['idpayCode']


@when('the citizen {citizen_name} regenerates the IDPay Code')
@given('the citizen {citizen_name} regenerates the IDPay Code')
def step_idpay_code_regenerate(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io)
    assert res.status_code == 200
    assert res.json()['idpayCode'] != context.idpay_code[citizen_name]

    context.old_idpay_code[citizen_name] = context.idpay_code[citizen_name]
    context.idpay_code[citizen_name] = res.json()['idpayCode']


@given('the IDPay Code is {status} for citizen {citizen_name}')
@then('the IDPay Code is {status} for citizen {citizen_name}')
def step_check_idpay_code_status(context, status, citizen_name):
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = get_idpay_code_status(token=token_io)
    assert res.status_code == 200

    if status == 'ENABLED':
        assert res.json()['isIdPayCodeEnabled'] is True
    elif status == 'NOT ENABLED':
        assert res.json()['isIdPayCodeEnabled'] is False


@when('the citizen {citizen_name} enrolls a new IDPay Code on the initiative')
@given('the citizen {citizen_name} enrolls a new IDPay Code on the initiative')
def step_citizen_enroll_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io,
                                   body={'initiativeId': context.initiative_id})

    assert res.status_code == 200
    context.idpay_code[citizen_name] = res.json()['idpayCode']

    step_check_idpay_code_status(context=context, status='enabled', citizen_name=citizen_name)


@given('the citizen {citizen_name} enrolls correctly a new IDPay Code on the initiative')
def step_citizen_enroll_correctly_idpay_code(context, citizen_name):
    step_citizen_enroll_idpay_code(context=context, citizen_name=citizen_name)
    step_check_status_instrument_idpay_code(context=context, citizen_name=citizen_name, status='ACTIVE')


@given('the citizen {citizen_name} uses its IDPay Code on the initiative')
@when('the citizen {citizen_name} uses its IDPay Code on the initiative')
def step_citizen_enable_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    assert res.status_code == 200


@when('the citizen {citizen_name} tries to use its IDPay Code on the initiative')
def step_citizen_try_enable_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    context.latest_idpay_code_enabling_response = res


@then('the latest IDPay Code enabling fails because {cause_ko}')
def step_check_latest_idpay_code_enabling_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CODE IS MISSING':
        assert context.latest_idpay_code_enabling_response.status_code == 403
        assert context.latest_idpay_code_enabling_response.json()['code'] == 403
        assert context.latest_idpay_code_enabling_response.json()['message'] == 'IdpayCode must be generated'


@when('the citizen {citizen_name} tries to enroll a new IDPay Code on the initiative')
def step_citizen_try_enroll_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io, body={'initiativeId': context.initiative_id})

    context.latest_idpay_code_enabling_response = res


@then('the latest IDPay Code enrollment fails because {cause_ko}')
def step_check_latest_idpay_code_enrollment_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CITIZEN IS NOT ONBOARD':
        assert context.latest_idpay_code_enabling_response.status_code == 404
        assert context.latest_idpay_code_enabling_response.json()['code'] == 404
        assert context.latest_idpay_code_enabling_response.json()[
                   'message'] == 'The requested initiative is not active for the current user!'
    elif cause_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_idpay_code_enabling_response.status_code == 400
        assert context.latest_idpay_code_enabling_response.json()['code'] == 400
        assert context.latest_idpay_code_enabling_response.json()[
                   'message'] == 'You are unsubscribed at this initiative!'


@given('the citizen {citizen_name} disables the IDPay Code from the initiative')
@when('the citizen {citizen_name} disables the IDPay Code from the initiative')
def step_citizen_disable_idpay_code(context, citizen_name):
    initiative_id = context.initiative_id
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 200
    assert res.json()['instrumentList'] != []

    instrument_idpay_code = None
    for instrument in res.json()['instrumentList']:
        if instrument['instrumentType'] == 'IDPAYCODE':
            instrument_idpay_code = instrument

    assert instrument_idpay_code is not None
    instrument_id = instrument_idpay_code['instrumentId']

    res = remove_payment_instrument(initiative_id=initiative_id, token=token_io, instrument_id=instrument_id)
    assert res.status_code == 200


@when('the citizen {citizen_name} tries to disable the IDPay Code on the initiative')
def step_citizen_try_disable_idpay_code(context, citizen_name):
    initiative_id = context.initiative_id
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 200
    assert res.json()['instrumentList'] != []

    instrument_idpay_code = None
    for instrument in res.json()['instrumentList']:
        if instrument['instrumentType'] == 'IDPAYCODE':
            instrument_idpay_code = instrument

    if instrument_idpay_code is not None:
        instrument_id = instrument_idpay_code['instrumentId']
    else:
        instrument_id = sha256(f'{citizen_name}'.encode()).hexdigest().lower()[:24]

    res = remove_payment_instrument(initiative_id=initiative_id, token=token_io, instrument_id=instrument_id)
    context.latest_response_idpay_code_deactivation = res


@then('the latest IDPay Code deactivation fails because {cause_ko}')
def step_check_latest_response_idpay_code_deactivation(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE INSTRUMENT IS NOT ACTIVE':
        assert context.latest_response_idpay_code_deactivation.status_code == 404
        assert context.latest_response_idpay_code_deactivation.json()['code'] == 404
        assert context.latest_response_idpay_code_deactivation.json()[
                   'message'] == 'The selected payment instrument is not active for such user and initiative.'


@given('the instrument IDPay Code is in {status} status for citizen {citizen_name} on initiative')
@then('the instrument IDPay Code is in {status} status for citizen {citizen_name} on initiative')
def step_check_status_instrument_idpay_code(context, status, citizen_name):
    initiative_id = context.initiative_id
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    if status == 'ACTIVE':
        retry_payment_instrument(expected_type=instrument_types.idpaycode, expected_status='ACTIVE',
                                 request=get_payment_instruments, token=token_io, initiative_id=initiative_id,
                                 field_type='instrumentType', field_status='status', num_required=1, tries=50, delay=2)

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Card not enrolled')

    elif status == 'ACTIVE AGAIN':
        retry_payment_instrument(expected_type=instrument_types.idpaycode, expected_status='ACTIVE',
                                 request=get_payment_instruments, token=token_io, initiative_id=initiative_id,
                                 field_type='instrumentType', field_status='status', num_required=1, tries=50, delay=2)

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=2, tries=50,
                       delay=2, message='Card not enrolled')

    elif status == 'DELETED':
        retry_timeline(expected=timeline_operations.delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Delete card rejected')

    elif status == 'REJECTED ADD':
        retry_timeline(expected=timeline_operations.rejected_add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Add card not rejected')

    elif status == 'REJECTED DELETE':
        retry_timeline(expected=timeline_operations.rejected_delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Delete card not rejected')


def step_create_authorize_request_trx_request_by_pos(pin: str, second_factor: str) -> (str, str):
    """
    This function is mocking a request from the POS to authorize a transaction payable by IDPay Code.
    Here the pin block is calculated.

    Returns:
        pin_block : str
            The pin block calculated from pin and second factor about IDPay Code
        key_encrypted: str
            The key that encrypts the data block which is in turn encrypted with IDPay public key
    """
    pin_bytes = binascii.a2b_hex(pin + "F" * (16 - len(pin)))
    second_factor_bytes = binascii.a2b_hex(second_factor)

    data_block_bytes = tools.xor(pin_bytes, second_factor_bytes)
    data_block = codecs.encode(data_block_bytes, 'hex').decode('utf-8')

    cipher = AES.new(bytes(KEY, 'utf-8'), AES.MODE_CBC, IV)
    pin_block_bytes = cipher.encrypt(pad(data_block.encode('utf-8'), AES.block_size))
    pin_block = codecs.encode(pin_block_bytes, 'hex').decode('utf-8')

    cipher = PKCS1_OAEP.new(RSA.import_key(PEM_KEY))
    key_encrypted_bytes = cipher.encrypt(KEY.encode())
    key_encrypted = b64encode(key_encrypted_bytes).decode('utf-8')

    return pin_block, key_encrypted


@given(
    'the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents through MIL (new)')
def step_when_merchant_generated_a_transaction_mil(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.latest_merchant_create_transaction_mil = post_merchant_create_transaction_mil(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_fiscal_code=curr_merchant_fiscal_code
    )
    # TODO fix with detail of trx (new)
    context.transactions[trx_name] = context.latest_merchant_create_transaction_mil

    step_check_transaction_status(context=context, trx_name=trx_name, expected_status='CREATED')
    context.associated_merchant[trx_name] = merchant_name

    check_unprocessed_transactions(initiative_id=context.initiative_id,
                                   expected_trx_id=context.transactions[trx_name]['id'],
                                   expected_effective_amount=context.transactions[trx_name]['amountCents'],
                                   expected_reward_amount=0,
                                   merchant_id=curr_merchant_id,
                                   expected_status='CREATED'
                                   )


@then('the transaction {trx_name} was {expected_status} for citizen')
def step_check_transaction_status(context, trx_name, expected_status):
    status = expected_status.upper()

    if status == 'CREATED':
        assert context.latest_merchant_create_transaction_mil.status_code == 200
        assert context.latest_merchant_create_transaction_mil.json()['status'] == 'CREATED'
        return

    if status == 'AUTHORIZED':
        assert context.latest_merchant_authorize_transaction_mil.status_code == 200
        assert context.transactions[trx_name]['status'] == 'AUTHORIZED'


@given('the MinInt associates the transaction {trx_name} with the citizen {citizen_name} by IDPay Code')
def step_minint_associates_trx_with_citizen(context, trx_name, citizen_name):
    response = put_minint_associate_user_and_payment(fiscal_code=context.citizens_fc[citizen_name],
                                                     transaction_id=context.transactions[trx_name]['id'])

    assert response.status_code == 200
    assert response.json()['status'] == 'IDENTIFIED'


@when('the MinInt tries to associate the transaction {trx_name} with the citizen {citizen_name} by IDPay Code')
def step_minint_tries_to_associate_trx_with_citizen(context, trx_name, citizen_name):
    response = put_minint_associate_user_and_payment(fiscal_code=context.citizens_fc[citizen_name],
                                                     transaction_id=context.transactions[trx_name]['id'])
    context.latest_minint_association = response


@then('the latest association by MinInt fails because citizen {citizen_name} is {reason_ko}')
def step_check_latest_association_with_citizen_by_minint(context, citizen_name, reason_ko):
    reason_ko = reason_ko.upper()
    curr_tokenized_fc = tokenize_fc(context.citizens_fc[citizen_name])

    if reason_ko == 'SUSPENDED':
        assert context.latest_minint_association.status_code == 403
        assert context.latest_minint_association.json()['code'] == 'PAYMENT_USER_SUSPENDED'
        assert context.latest_minint_association.json()[
                   'message'] == f'User {curr_tokenized_fc} has been suspended for initiative {context.initiative_id}'
    elif reason_ko == 'UNSUBSCRIBED':
        assert context.latest_minint_association.status_code == 403
        assert context.latest_minint_association.json()['code'] == 'PAYMENT_USER_SUSPENDED'
        assert context.latest_minint_association.json()[
                   'message'] == f'User {curr_tokenized_fc} has been suspended for initiative {context.initiative_id}'


@then('the latest association by MinInt fails because the transaction {trx_name} is {reason_ko}')
def step_check_latest_association_by_minint(context, trx_name, reason_ko):
    reason_ko = reason_ko.upper()
    trx_id = context.transactions[trx_name]['id']
    trx_code = context.transactions[trx_name]['trxCode']

    if reason_ko == 'EXPIRED':
        assert context.latest_minint_association.status_code == 404
        assert context.latest_minint_association.json()['code'] == 'PAYMENT_NOT_FOUND_EXPIRED'
        assert context.latest_minint_association.json()[
                   'message'] == f'Cannot find transaction with transactionId [{trx_id}]'
    elif reason_ko == 'ALREADY AUTHORIZED':
        assert context.latest_minint_association.status_code == 403
        assert context.latest_minint_association.json()['code'] == 'PAYMENT_USER_NOT_VALID'
        assert context.latest_minint_association.json()[
                   'message'] == f'Transaction with trxCode [{trx_code}] is already assigned to another user'


@when('the merchant {merchant_name} pre-authorizes and authorizes the transaction {trx_name} with IDPay Code '
      '{correctness} inserted by citizen {citizen_name}')
@given('the merchant {merchant_name} pre-authorizes and authorizes the transaction {trx_name} with IDPay Code '
       '{correctness} inserted by citizen {citizen_name}')
def step_pre_and_auth_trx_mil(context, merchant_name, trx_name, correctness, citizen_name):
    step_tries_to_pre_authorize_transaction_mil(merchant_name=merchant_name, trx_name=trx_name)

    assert context.latest_merchant_pre_authorize_transaction_mil.status_code == 200
    second_factor = context.latest_merchant_pre_authorize_transaction_mil.json()['secondFactor']
    assert second_factor is not None

    correctness = correctness.upper()

    if correctness == "CORRECTLY":
        step_auth_trx_mil(context=context, trx_name=trx_name, merchant_name=merchant_name,
                          pin=context.idpay_code[citizen_name], second_factor=second_factor)

        assert context.latest_merchant_authorize_transaction_mil.status_code == 200
        context.transactions[trx_name] = context.latest_merchant_authorize_transaction_mil

    elif correctness == 'INCORRECTLY':
        step_auth_trx_mil(context=context, trx_name=trx_name, merchant_name=merchant_name,
                          pin=context.old_idpay_code[citizen_name] or random.randint(10000, 20000),
                          second_factor=second_factor)
        step_check_latest_auth_fails(context=context, reason_ko='THE IDPAY CODE IS INCORRECT')


def step_auth_trx_mil(context, trx_name, merchant_name, pin, second_factor):
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    trx_id = context.transactions[trx_name]['id']
    pin_block, encrypted_key = step_create_authorize_request_trx_request_by_pos(pin=pin,
                                                                                second_factor=second_factor)

    context.latest_merchant_authorize_transaction_mil = put_merchant_authorize_transaction_mil(
        transaction_id=trx_id,
        merchant_fiscal_code=curr_merchant_fiscal_code,
        pin_block=pin_block,
        encrypted_key=encrypted_key)


@then('the latest authorization fails because {reason_ko}')
def step_check_latest_auth_fails(context, reason_ko):
    reason_ko = reason_ko.upper()
    if reason_ko == 'THE IDPAY CODE IS INCORRECT':
        assert context.latest_merchant_authorize_transaction_mil.status_code == 403
        assert context.latest_merchant_authorize_transaction_mil.json()['message'] == 'PAYMENT_INVALID_PINBLOCK'


@when('the merchant {merchant_name} tries to pre-authorize the transaction {trx_name} with IDPay Code')
def step_tries_to_pre_authorize_transaction_mil(context, merchant_name, trx_name):
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    trx_id = context.transactions[trx_name]['id']

    context.latest_merchant_pre_authorize_transaction_mil = put_merchant_pre_authorize_transaction_mil(
        transaction_id=trx_id,
        merchant_fiscal_code=curr_merchant_fiscal_code)
