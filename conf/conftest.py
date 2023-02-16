"""Configuration function that executes before tests.
"""
from conf.configuration import settings
from util.utils import TextFormat


def pytest_configure():
    """Configuration function that executes before tests.
    """
    print(f"Testing environment: "
          f"{TextFormat.BOLD}{TextFormat.HEADER}{settings['TARGET_ENV'].upper()}{TextFormat.ENDC}")
