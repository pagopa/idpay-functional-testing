import time

import pytest

from api.idpay import timeline, enroll_iban
from api.issuer import enroll
from api.onboarding_io import accept_terms_and_condition, check_prerequisites, pdnd_autocertification, status_onboarding
from api.token_io import login, introspect
from conf.configuration import secrets
from util.certs_loader import load_pm_public_key
from util.encrypt_utilities import pgp_string_routine


def get_io_token(fc):
    """Onboarding process through IO
    """
    return login(fc).content.decode('utf-8')


def onboard_io(fc):
    """Onboarding process through IO
    """
    res = login(fc)
    token = res.content.decode('utf-8')
    res = introspect(token)
    assert res.json()['fiscal_code'] == fc

    res = accept_terms_and_condition(token, secrets.initiatives.cashback_like.id)
    assert res.status_code == 204

    res = check_prerequisites(token, secrets.initiatives.cashback_like.id)
    assert res.status_code == 200

    res = pdnd_autocertification(token, secrets.initiatives.cashback_like.id)
    assert res.status_code == 202

    res = status_onboarding(token, secrets.initiatives.cashback_like.id)
    assert res.status_code == 200

    retry_io_onboarding(expected='ONBOARDING_OK', request=status_onboarding, token=token,
                        initiative_id=secrets.initiatives.cashback_like.id, field='status', tries=10, delay=3,
                        message='Citizen onboard not OK')

    return status_onboarding(token, secrets.initiatives.cashback_like.id)


def iban_enroll(token, iban):
    res = enroll_iban(secrets.initiatives.cashback_like.id,
                      token,
                      {
                          "iban": iban,
                          "description": "conto di test"
                      }
                      )
    assert res.status_code == 200

    retry_timeline(expected='ADD_IBAN', request=timeline, token=token,
                   initiative_id=secrets.initiatives.cashback_like.id, field='operationType', tries=10, delay=3,
                   message='IBAN not enrolled')

    return timeline(secrets.initiatives.cashback_like.id, token)


def card_enroll(fc, pan):
    res = enroll(secrets.initiatives.cashback_like.id,
                 fc,
                 {
                     "brand": "VISA",
                     "type": "DEB",
                     "pgpPan": pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     "expireMonth": "08",
                     "expireYear": "2023",
                     "issuerAbiCode": "03069",
                     "holder": "TEST"
                 }
                 )

    assert res.status_code == 200

    token = get_io_token(fc)

    retry_timeline(expected='ADD_INSTRUMENT', request=timeline, token=token,
                   initiative_id=secrets.initiatives.cashback_like.id, field='operationType', tries=10, delay=3,
                   message='Card not enrolled')

    return timeline(secrets.initiatives.cashback_like.id, token)


def retry_io_onboarding(expected, request, token, initiative_id, field, tries=3, delay=5, backoff=1,
                        message='Test failed'):
    count = 0
    res = request(token, initiative_id)
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            pytest.fail(f'{message} after {delay * (tries * backoff)}s')
        time.sleep(delay * (count * backoff))
        res = request(token, initiative_id)
        success = (expected == res.json()[field])


def retry_timeline(expected, request, token, initiative_id, field, tries=3, delay=5, backoff=1,
                   message='Test failed'):
    count = 0
    res = request(initiative_id, token)
    success = any(operation[field] == expected for operation in res.json()['operationList'])
    while not success:
        count += 1
        if count == tries:
            pytest.fail(f'{message} after {delay * (tries * backoff)}s')
        time.sleep(delay * (count * backoff))
        res = request(initiative_id, token)
        success = any(operation[field] == expected for operation in res.json()['operationList'])
