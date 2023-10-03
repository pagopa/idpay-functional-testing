"""Configuration function that executes before tests.
"""
import time

import pytest

from conf.configuration import secrets
from conf.configuration import settings
from util.text_formatter import TextFormat
from util.utility import create_initiative
from util.utility import delete_new_initiatives_after_test


def pytest_configure():
    """Configuration function that executes before tests.
    """
    secrets['newly_created'] = set()
    if secrets == {}:
        msg = f'{TextFormat.FAIL}Missing {settings.TARGET_ENV}' \
              f' section in {settings.SECRET_PATH}{TextFormat.ENDC}\n'
        pytest.exit(msg)
    print(f'Testing environment: '
          f"{TextFormat.BOLD}{TextFormat.HEADER}{settings['TARGET_ENV'].upper()}{TextFormat.ENDC}")

    create_test_initiatives('cashback_like')
    create_test_initiatives('not_started')
    create_test_initiatives('complex')
    time.sleep(settings.INITIATIVE_STARTUP_TIME_SECONDS)


def pytest_collection_modifyitems(items):
    """Configuration function that add "use_case" property for marked tests.
    """
    for item in items:
        for marker in item.iter_markers(name='use_case'):
            test_id = marker.args[0]
            item.user_properties.append(('use_case', test_id))


def pytest_sessionfinish(session, exitstatus):
    # This code will run once at the end of the pytest session
    delete_new_initiatives_after_test()


def create_test_initiatives(initiative_name: str):
    secrets.initiatives[initiative_name] = {}
    secrets.initiatives[initiative_name]['id'] = create_initiative(initiative_name_in_settings=initiative_name)
    print(f'Created initiative {secrets.initiatives[initiative_name]["id"]} ({initiative_name})')
    secrets['newly_created'].add(secrets.initiatives[initiative_name]['id'])
