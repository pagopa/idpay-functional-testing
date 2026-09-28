import datetime
import random
import uuid


def generate_merchant_name():
    return f"Esercente di test {datetime.datetime.now().strftime("%Y%m%d - %H%M%S")} {str(uuid.uuid4())[:4]}"


def generate_merchant_vat():
    return str(random.randint(10000000000, 99999999999))
