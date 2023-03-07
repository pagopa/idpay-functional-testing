"""Configuration function that executes before tests.
"""
import pytest

from conf.configuration import settings, secrets
from util.text_formatter import TextFormat


def pytest_configure():
    """Configuration function that executes before tests.
    """
    if secrets == {}:
        msg = f"{TextFormat.FAIL}Missing {settings.TARGET_ENV}" \
              f" section in {settings.SECRET_PATH}{TextFormat.ENDC}\n"
        pytest.exit(msg)
    print(f"Testing environment: "
          f"{TextFormat.BOLD}{TextFormat.HEADER}{settings['TARGET_ENV'].upper()}{TextFormat.ENDC}")
