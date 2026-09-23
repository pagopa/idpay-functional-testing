"""RDB consent scenarios use a fresh user ID to isolate acceptance state."""
import uuid

from behave import given
from behave import then
from behave import when

from api import asset_register as api
from util import rdb_dependencies as dependencies
from util import rdb_utilities as rdb


@given('a new RDB user authenticated as "{profile}"')
def rdb_new_user(context, profile):
    s = rdb.state(context)
    body = rdb.PROFILE_BUILDERS[profile]()
    body['uid'] = str(uuid.uuid4())
    s.bodies[profile] = body
    s.tokens[profile] = rdb.token_from_response(api.post_token_test(body))
    rdb.authenticate(context, profile)


@when('the RDB user requests the consent status')
def rdb_get_consent(context):
    s = rdb.state(context)
    s.response = api.get_portal_consent(s.token)


@given('the RDB user knows the current consent version')
def rdb_current_consent(context):
    rdb_get_consent(context)
    s = rdb.state(context)
    s.consent = rdb.success(s.response).json()
    assert s.consent.get('versionId'), 'Use a user who has not accepted the current consent'


@given('the RDB user has accepted the current consent version')
def rdb_accepted_consent(context):
    rdb_current_consent(context)
    rdb_save_consent(context)
    rdb.success(rdb.state(context).response)


@when('the RDB user accepts the current consent version')
def rdb_save_consent(context):
    s = rdb.state(context)
    s.response = api.save_portal_consent(s.token, s.consent['versionId'], s.consent['firstAcceptance'])


@when('the RDB user accepts an outdated consent version')
def rdb_old_consent(context):
    s = rdb.state(context)
    # A non-current version is sufficient to exercise the version mismatch contract.
    version = rdb.config().get('outdated_consent_version', str(uuid.uuid4()))
    assert version != s.consent['versionId']
    s.response = api.save_portal_consent(s.token, version, s.consent['firstAcceptance'])


@then('the RDB consent requires first acceptance of the current version')
def rdb_first_consent(context):
    body = rdb.success(rdb.state(context).response).json()
    assert body['firstAcceptance'] is True and body['versionId']


@then('the RDB consent requires renewed acceptance of the current version')
def rdb_renew_consent(context):
    s = rdb.state(context)
    body = rdb.success(s.response).json()
    assert body['firstAcceptance'] is False
    assert body['versionId'] == rdb.required(s.dataset, 'current_version')
    assert body['versionId'] != rdb.required(s.dataset, 'previous_version')


@then('no RDB consent acceptance is required')
def rdb_no_consent(context):
    assert rdb.success(rdb.state(context).response).json() == {}


@then('no RDB consent acceptance is required after reading it again')
def rdb_read_accepted_consent(context):
    rdb_get_consent(context)
    rdb_no_consent(context)


@then('the RDB consent still requires first acceptance')
def rdb_consent_not_saved(context):
    s = rdb.state(context)
    rdb_get_consent(context)
    rdb_first_consent(context)
    assert s.response.json()['versionId'] == s.consent['versionId']


@given('the RDB dependency "{name}" is unavailable')
def rdb_dependency_unavailable(context, name):
    dependencies.fail_dependency(context, name)


@then('the RDB consent request fails because OneTrust is unavailable')
def rdb_consent_dependency_error(context):
    s = rdb.state(context)
    expected = dependencies.dependency('OneTrust').get('expected_http_status', 500)
    rdb.success(s.response, expected)
    dependencies.assert_fault_observed(context, 'OneTrust')


@then('the RDB consent still requires first acceptance after OneTrust recovers')
def rdb_consent_after_recovery(context):
    dependencies.restore_dependency(context, 'OneTrust')
    rdb_consent_not_saved(context)
