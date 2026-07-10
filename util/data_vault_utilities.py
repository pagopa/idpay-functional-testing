from api.data_vault import data_vault_tokenize, data_vault_detokenize

def tokenize_fc(fiscal_code: str):
    res = data_vault_tokenize(pii=fiscal_code)
    assert res.status_code == 200
    token = res.json()['token']
    res = data_vault_detokenize(token=token)
    assert res.json()['pii'] == fiscal_code
    return token


def detokenize_to_fc(token: str):
    res = data_vault_detokenize(token=token)
    assert res.status_code == 200
    fiscal_code = res.json()['pii']
    res = data_vault_tokenize(pii=fiscal_code)
    assert res.status_code == 200
    assert res.json()['token'] == token
    return fiscal_code