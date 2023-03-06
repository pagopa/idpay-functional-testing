"""Endpoint tests
"""
import pytest
from faker import Faker

from api.token_io import introspect, login

fake = Faker('it_IT')


@pytest.mark.IO
def test_login_io():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """

    fake_cf = fake.ssn()
    my_fiscal_code = f'{fake_cf[:11]}X000{fake_cf[15:]}'

    res = login("https://api-io.uat.cstar.pagopa.it/bpd/pagopa/api/v1/login", my_fiscal_code)
    token = res.content.decode('utf-8')
    res = introspect("https://api-io.uat.cstar.pagopa.it/bpd/pagopa/api/v1/user", token)

    assert res.json()['fiscal_code'] == my_fiscal_code
