import time

from api.onboarding_io import save_onboarding
from api.onboarding_io import status_onboarding
from api.token_io import login

def get_io_token(fc):
    """Login through IO
    :param fc: fiscal code to log in.
    """
    return login(fc).content.decode('utf-8')

def onboard_io(fc, initiative_id):
    """Onboarding process through IO
    :param fc: fiscal code to onboard
    :param initiative_id: ID of the initiative of interest.
    """
    token = get_io_token(fc)

    res = save_onboarding(token, initiative_id)
    assert res.status_code == 202

    retry_io_onboarding(expected='ACCEPTED_TC', request=status_onboarding, token=token,
                        initiative_id=initiative_id, field='status', tries=50, delay=1,
                        message='Citizen not ACCEPTED_TC')

    res = status_onboarding(token, initiative_id)
    assert res.status_code == 200

    res = retry_io_onboarding(expected='ONBOARDING_OK', request=status_onboarding, token=token,
                              initiative_id=initiative_id, field='status', tries=50, delay=1,
                              message='Citizen onboard not OK')
    return res

def retry_io_onboarding(expected, request, token, initiative_id, field, tries=3, delay=5,
                        message='Test failed'):
    count = 0
    res = request(token, initiative_id)
    assert res.status_code == 200, (
        f'Onboarding status request failed: {res.status_code} {res.text}'
    )
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(token, initiative_id)
        assert res.status_code == 200, (
            f'Onboarding status request failed: {res.status_code} {res.text}'
        )
        success = (expected == res.json()[field])
    actual = res.json()[field]

    assert expected == actual, (
        f'result retry io onboarding {res.json()[field]} does not match expected {expected} for field {field}'
    )

    return res

def build_bonus_elettrodomestici_self_declaration_list_payload(multi_consent_isee_value:str='1', self_declaration_accepted=True):
    return [{
            '_type': 'multi_consent',
            'code': 'isee',
            'value': multi_consent_isee_value
        },
        {
            '_type': 'boolean',
            'accepted': self_declaration_accepted,
            'code': '1'
        }]

def build_bonus_decoder_self_declaration_list_payload(multi_consent_isee_value:str='1'):
    return [{
            '_type': 'multi_consent',
            'code': 'isee',
            'value': multi_consent_isee_value
        }]

def build_boolean_self_declaration_list_payload(self_declaration_accepted=True):
    return [{
            '_type': 'boolean',
            'accepted': self_declaration_accepted,
            'code': '1'
        }]

def build_self_declaration_list_payload_by_initiative(
    initiative_name: str,
    multi_consent_isee_value: str,
    self_declaration_accepted=True,
):
    match initiative_name:
        case 'bonus_elettrodomestici':
            return build_bonus_elettrodomestici_self_declaration_list_payload(
                multi_consent_isee_value=multi_consent_isee_value,
                self_declaration_accepted=self_declaration_accepted,
            )
        case 'bonus_decoder':
            return build_bonus_decoder_self_declaration_list_payload(
                multi_consent_isee_value=multi_consent_isee_value,
            )
        case _:
            return None
