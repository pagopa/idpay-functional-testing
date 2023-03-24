import random
from math import floor

import pytest

from api.idpay import timeline, wallet
from conf.configuration import secrets, settings
from util import dataset_utility
from util.dataset_utility import fake_fc, fake_pan
from util.transaction_upload import encrypt_and_upload
from util.utility import onboard_io, card_enroll, get_io_token, iban_enroll, retry_timeline, transactions_hash, \
    custom_transaction, clean_trx_files

initiative_id = secrets.initiatives.cashback_like.id
cashback_percentage = settings.initiatives.cashback_like.cashback_percentage
max_cashback = settings.initiatives.cashback_like.max_cashback
max_amount = (max_cashback / cashback_percentage * 100) * 100


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.4')
def test_send_transaction():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'
    assert any(operation['operationType'] == 'ADD_INSTRUMENT' for operation in
               card_enroll(test_fc, pan, initiative_id).json()['operationList'])

    token = get_io_token(test_fc)
    assert any(
        operation['operationType'] == 'ADD_IBAN' for operation in
        iban_enroll(token, curr_iban, initiative_id).json()['operationList'])

    # Send the transaction
    amount = floor(random.random() * max_amount)

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)
