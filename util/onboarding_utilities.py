import time

from api.token_io import login

def get_io_token(fc):
    """Login through IO
    :param fc: fiscal code to log in.
    """
    return login(fc).content.decode('utf-8')


def retry_io_onboarding(expected, request, token, initiative_id, field, tries=3, delay=5,
                        message='Test failed'):
    count = 0
    success = False
    while not success:
        if count == tries:
            break
        time.sleep(delay)
        res = request(token, initiative_id)
        assert res.status_code != 500, (
            f'Onboarding status request failed: {res.status_code} {res.text}'
        )
        success = field in res.json() and expected == res.json()[field]
        count += 1

    assert field in res.json(), (
        f'Onboarding status response does not contain expected field: {field}, response: {res.json()}'
    )

    actual = res.json()[field]
    assert expected == actual, (
        f'{message}: result retry io onboarding {actual} does not match expected {expected} for field {field}'
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

def build_bonus_decoder_self_declaration_list_payload():
    return []

def build_budget_exhausted_self_declaration_list_payload(self_declaration_accepted=True):
    return [{
            '_type': 'boolean',
            'accepted': self_declaration_accepted,
            'code': '1'
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
            return build_bonus_decoder_self_declaration_list_payload()
        case 'budget_exhausted':
            return build_budget_exhausted_self_declaration_list_payload(
                self_declaration_accepted=self_declaration_accepted
            )
        case _:
            return None
