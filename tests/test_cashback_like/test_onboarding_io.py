"""Onboard tests
"""
import pytest

from conf.configuration import secrets
from util.dataset_utility import fake_fc
from util.utility import onboard_io


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.1')
def test_onboard_io():
    """Onboarding process through IO
    """

    test_fc = fake_fc()

    assert onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()['status'] == 'ONBOARDING_OK'