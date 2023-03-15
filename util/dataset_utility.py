import random
from hashlib import sha256

from faker import Faker

from api.rtd import pm_salt

fake = Faker('it_IT')

circuits = ['visa', 'mastercard', 'maestro', 'amex']


def hash_pan(pan: str):
    salt = pm_salt()
    return sha256(f"{pan}{salt}".encode()).hexdigest()


def fake_fc():
    """Faker wrapper that calls faker's ssn method and uses non-existing birthplace characters.
        """
    fake_cf = fake.ssn()
    return f'{fake_cf[:11]}X000{fake_cf[15:]}'


def fake_pan():
    """Faker wrapper that calls faker's credit_card_number method and random circuit.
            """
    return fake.credit_card_number(random.choice(circuits))
