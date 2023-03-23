import math
import random
from hashlib import sha256

from faker import Faker
from schwifty import IBAN

from api.rtd import pm_salt

fake = Faker('it_IT')

circuits = ['visa', 'mastercard', 'maestro', 'amex']


def hash_pan(pan: str):
    """Function that hashes a PAN with salt got from the Payment Manager
    :param pan: Clear PAN to be encrypted.
    :returns:  The hashed  PAN.
    :rtype: str
    """
    salt = pm_salt()
    return sha256(f"{pan}{salt}".encode()).hexdigest()


def fake_fc():
    """Faker wrapper that calls faker's ssn method and uses non-existing birthplace characters.
    :returns:  A fake fiscal code.
    :rtype: str
    """
    fake_cf = fake.ssn()
    return f'{fake_cf[:11]}X000{fake_cf[15:]}'


def fake_pan():
    """Faker wrapper that calls faker's credit_card_number method and random circuit.
    :returns:  A fake PAN.
    :rtype: str
    """
    return fake.credit_card_number(random.choice(circuits))


def fake_iban(abi):
    """Wrapper that calls schwifty's IBAN method with arbitrary ABI code.
    :returns:  A fake IBAN.
    :rtype: str
    """
    return IBAN.generate('IT', bank_code=abi, account_code=str(round(random.random() * math.pow(10, 12)))).compact


def fake_vat():
    """Faker wrapper that calls faker's vat method.
    :returns: a fake VAT.
    :rtype: str
    """
    return fake.company_vat()[2:]
