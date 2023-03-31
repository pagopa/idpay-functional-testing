"""Configuration function that executes before tests.
"""
import pytest

from conf.configuration import secrets
from conf.configuration import settings
from util.text_formatter import TextFormat


def pytest_configure():
    """Configuration function that executes before tests.
    """
    if secrets == {}:
        msg = f'{TextFormat.FAIL}Missing {settings.TARGET_ENV}' \
              f' section in {settings.SECRET_PATH}{TextFormat.ENDC}\n'
        pytest.exit(msg)
    print(f'Testing environment: '
          f"{TextFormat.BOLD}{TextFormat.HEADER}{settings['TARGET_ENV'].upper()}{TextFormat.ENDC}")


def pytest_collection_modifyitems(items):
    """Configuration function that add "use_case" property for marked tests.
    """
    for item in items:
        for marker in item.iter_markers(name='use_case'):
            test_id = marker.args[0]
            item.user_properties.append(('use_case', test_id))
