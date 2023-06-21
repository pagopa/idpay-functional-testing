import time

from behave import given
from behave import when


@given('{waiting_seconds} second/s pass')
@when('{waiting_seconds} second/s pass')
def step_waiting_seconds(context, waiting_seconds):
    time.sleep(float(waiting_seconds))
