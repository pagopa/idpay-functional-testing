"""Card enrollment tests
"""
import math
import random
import string

import pytest

from api.idpay import get_payment_instruments
from api.idpay import remove_payment_instrument
from api.idpay import unsubscribe
from api.idpay import wallet
from api.issuer import enroll
from conf.configuration import secrets
from conf.configuration import settings
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_fc
from util.dataset_utility import fake_pan
from util.encrypt_utilities import pgp_string_routine
from util.utility import card_enroll
from util.utility import card_removal
from util.utility import get_io_token
from util.utility import onboard_io
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enrollment_api_issuer():
    """Card enrollment process through Issuer API.
    """
    test_fc = fake_fc()
    pan = fake_pan()

    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()
    card_enroll(test_fc, pan, secrets.initiatives.cashback_like.id).json()


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_fail_enrollment_issuer_not_onboard():
    """This test tries to enroll a card without being onboard.
    """
    test_fc = fake_fc()
    pan = fake_pan()
    res = enroll(secrets.initiatives.cashback_like.id,
                 test_fc,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )
    assert res.status_code == 404


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.card_removal
def test_remove_payment_instrument_of_another_citizen():
    """This test tries to remove a card enrolled by another citizen.
    """
    initiative_id = secrets.initiatives.cashback_like.id
    test_fc1 = fake_fc()
    pan = fake_pan()
    test_fc2 = fake_fc()
    token1 = get_io_token(test_fc1)
    token2 = get_io_token(test_fc2)

    onboard_io(test_fc1, secrets.initiatives.cashback_like.id).json()
    onboard_io(test_fc2, secrets.initiatives.cashback_like.id).json()

    card_enroll(test_fc1, pan, secrets.initiatives.cashback_like.id).json()

    res = get_payment_instruments(initiative_id=initiative_id, token=token1)
    assert res.status_code == 200
    instrument_id = res.json()['instrumentList'][0]['instrumentId']

    res = remove_payment_instrument(initiative_id=initiative_id, token=token2, instrument_id=instrument_id)
    assert res.status_code == 404


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enroll_same_payment_instrument_of_another_citizen():
    """This test tries to enroll a card enrolled by another citizen.
    """
    initiative_id = secrets.initiatives.cashback_like.id
    test_fc1 = fake_fc()
    pan = fake_pan()
    test_fc2 = fake_fc()
    onboard_io(test_fc1, secrets.initiatives.cashback_like.id).json()
    onboard_io(test_fc2, secrets.initiatives.cashback_like.id).json()

    card_enroll(test_fc1, pan, secrets.initiatives.cashback_like.id).json()

    res = enroll(initiative_id,
                 test_fc2,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )

    assert res.status_code == 403
    assert res.json()['message'] == 'Payment instrument already associated to another citizen'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enroll_blank_pan():
    """Card enrollment process through Issuer API.
    """
    test_fc = fake_fc()
    pan = ''

    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()

    res = enroll(secrets.initiatives.cashback_like.id,
                 test_fc,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )

    assert res.status_code == 400
    assert res.reason == 'ErrorPM'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enroll_incorrect_length_pan_too_short():
    """This test tries to enroll cards that have not the correct length (less than the minimum size of 12).
    """
    test_fc = fake_fc()

    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()

    for i in range(12):
        pan = fake_pan()[:i]
        res = enroll(secrets.initiatives.cashback_like.id,
                     test_fc,
                     {
                         'brand': 'VISA',
                         'type': 'DEB',
                         'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                         'expireMonth': '08',
                         'expireYear': '2023',
                         'issuerAbiCode': '03069',
                         'holder': 'TEST'
                     }
                     )
        assert res.status_code == 400
        assert res.reason == 'ErrorPM'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enroll_incorrect_length_pan_too_long():
    """This test tries to enroll cards that have not the correct length (exceeds the allowed size of 20).
    """
    test_fc = fake_fc()

    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()
    for i in range(21, 30):
        curr_pan = str(math.floor(random.random() * math.pow(10, 30)))[:i].zfill(i)
        print(len(curr_pan))
        res = enroll(secrets.initiatives.cashback_like.id,
                     test_fc,
                     {
                         'brand': 'VISA',
                         'type': 'DEB',
                         'pgpPan': pgp_string_routine(curr_pan,
                                                      load_pm_public_key()).decode('unicode_escape'),
                         'expireMonth': '08',
                         'expireYear': '2023',
                         'issuerAbiCode': '03069',
                         'holder': 'TEST'
                     }
                     )
        assert res.status_code == 400
        assert res.reason == 'ErrorPM'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
def test_enroll_alphabetic_characters_pan():
    """This test tries to enroll cards that have alphabetic characters.
    """
    test_fc = fake_fc()
    pan = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()
    card_enroll(test_fc, pan, secrets.initiatives.cashback_like.id).json()


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.need_fix
def test_fail_enrollment_card_expired():
    """This test tries to enroll an expired cards.
    """
    test_fc = fake_fc()
    pan = fake_pan()
    onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()
    res = enroll(secrets.initiatives.cashback_like.id,
                 test_fc,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '01',
                     'expireYear': '2000',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )
    assert res.status_code == 400
    assert res.reason == 'ErrorPM'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.unsubscribe
def test_cannot_enroll_same_payment_instrument_of_another_unsubscribed_citizen():
    """This test tries to enroll a card enrolled by another citizen that unsubscribed the initiative.
    """
    initiative_id = secrets.initiatives.cashback_like.id
    pan = fake_pan()
    test_fc1 = fake_fc()
    token1 = get_io_token(test_fc1)
    test_fc2 = fake_fc()
    onboard_io(test_fc1, secrets.initiatives.cashback_like.id).json()
    onboard_io(test_fc2, secrets.initiatives.cashback_like.id).json()

    card_enroll(test_fc1, pan, secrets.initiatives.cashback_like.id).json()
    res = unsubscribe(initiative_id, token1)
    # 1.24.0
    assert res.status_code == 204
    # 1.24.0
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token1,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not unsubscribed')

    res = enroll(initiative_id,
                 test_fc2,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )

    assert res.status_code == 403
    assert res.json()['message'] == 'Payment instrument already associated to another citizen'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.card_removal
def test_cannot_enroll_same_payment_instrument_of_another_citizen_that_removed_it():
    """This test tries to enroll a card enrolled by another citizen that removed it.
    """
    initiative_id = secrets.initiatives.cashback_like.id
    pan = fake_pan()
    test_fc1 = fake_fc()
    test_fc2 = fake_fc()
    onboard_io(test_fc1, secrets.initiatives.cashback_like.id).json()
    onboard_io(test_fc2, secrets.initiatives.cashback_like.id).json()

    card_enroll(test_fc1, pan, secrets.initiatives.cashback_like.id).json()
    card_removal(test_fc1, initiative_id)

    res = enroll(initiative_id,
                 test_fc2,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )
    assert res.status_code == 403
    assert res.json()['message'] == 'Payment instrument already associated to another citizen'
