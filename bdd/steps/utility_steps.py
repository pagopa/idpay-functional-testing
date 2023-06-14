import time

from behave import when


@when('{waiting_seconds} second/s pass')
def step_waiting_seconds(context, waiting_seconds):
    time.sleep(float(waiting_seconds))
