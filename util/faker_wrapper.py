"""Utility class that wraps faker.
"""
from faker import Faker

fake = Faker('it_IT')


def fake_fc():
    """Faker wrapper that calls faker's ssn method and uses non-existing birthplace characters.
        """
    fake_cf = fake.ssn()
    return f'{fake_cf[:11]}X000{fake_cf[15:]}'
