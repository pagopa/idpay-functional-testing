"""Check direct email service acceptance separately from RDB outage resilience."""
from behave import given, then, when

from api import rdb_email
from util import rdb_dependencies as dependencies
from util import rdb_notification_utilities as notifications
from util import rdb_utilities as rdb


@given('an RDB email service request of type "{kind}"')
def rdb_email_request(context, kind):
    rdb.state(context).email_request = notifications.request_payload(kind)


@when('the test invokes the RDB email notification service')
def rdb_invoke_email(context):
    config = notifications.service_config()
    s = rdb.state(context)
    s.email_response = rdb_email.notify(
        rdb.required(config, 'notify_url', 'asset_register.email_service'),
        s.email_request, notifications.request_headers(),
    )


@then('the RDB email notification service responds with HTTP 204')
def rdb_email_accepted(context):
    response = rdb.state(context).email_response
    assert response.status_code == 204, (
        f'Expected email service HTTP 204, got {response.status_code}'
    )
    assert not response.content, 'HTTP 204 must have no response body'


@then('the RDB backend received the email service failure')
def rdb_email_failure_observed(context):
    dependencies.assert_fault_observed(context, 'email')
