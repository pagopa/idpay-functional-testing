# RDB functional tests

The `bdd/features/bonus_elettrodomestici/rdb` suite contains 96 independent scenarios.
Steps use the APIs of the selected environment; generated datasets do not mock responses.
Latest full run with simplified cleanup: [UAT, 9 October 2026](rdb-test-results-2026-10-09-uat.md),
95 scenarios passed and 1 concurrency check failed, confirmed by an isolated rerun.
All 96 cleanups completed without hook errors.
The failure was subsequently fixed by moving preliminary checks outside the
concurrency window: both concurrent upload cases pass in two consecutive UAT runs.

## Running the tests

Install dependencies with `pipenv sync`. The default in `settings.yaml` is `uat`.
In PowerShell, explicitly select the environment:

```powershell
$env:PARI_TARGET_ENV = "uat"  # or "dev"
pipenv run behave --junit --junit-directory "tests/reports/behave" --tags "@rdb"
```

In the `test-run` workflow, select the environment, type `bdd`, and tag `rdb`.
To run a single scenario, use the feature path and `--name "^Scenario name$"`.

The file specified by `PARI_SECRET_PATH` (default: `conf/pari-feature-secrets.json`)
must contain a section for the selected environment. Imports require access
to the internal host, through a VPN when necessary.

`--dry-run` checks scenario-to-step matching without invoking APIs.
`@rdb_fixture` indicates a prerequisite; it does not exclude the scenario from the run.

## Configuration and secrets

Configure the following under `asset_register` in the environment JSON:

| Field | Purpose and confidentiality |
| --- | --- |
| `token_payload.operatore`, `.l1`, `.l2` | Existing profiles reused by the builders; keep personal and organizational data out of Git |
| `profiles` | Additional profiles with the same fields, including `orgRole`, `orgId`, `email`, `uid` |
| `initiatives.A`, `.B` | ID overrides; when absent, the environment's `initiatives.bonus_elettrodomestici.id` and `initiatives.bonus_decoder.id` are used |
| `base_path.IDPAY.internal` (outside `asset_register`) | Internal host already used by the suite; it must be reachable for `POST /idpayassetregisterbackend/idpay/register/producers`. No Data Factory key is required |
| `application_tokens.expired` | Optional signed, expired JWT; still treat it as a credential |
| `email_service` (optional) | Any additional `headers`; the token is generated from the configured profiles. The dummy recipient comes from `RDB_EMAIL_TEST_RECIPIENT` in settings. The URL uses `base_path.IO`, `IDPAY.domain`, and `IDPAY.endpoints.asset_register.notify_path` |
| `poll_timeout`, `poll_interval` | API polling settings, defaulting to 120 and 2 seconds; these are not secrets |

A and B must be configured for RDB with compatible templates and associations.
Use dedicated test producers without concurrent writes from other processes.
Profiles use `email` and `orgVAT`, with support for the aliases `orgEmail` and `orgVat`.
Keep credentials, JWTs, and personal data out of Git. Public URLs, initiative IDs,
and energy class thresholds are not credentials.

## Data written by the tests

The suite uses the real APIs of the selected environment. CSV uploads and validation
can create products, history records, and reports; imports and email updates modify
associations of dedicated producers. Consent and Invitalia datasets create dedicated
acceptance records and draft initiatives.
Generic hooks only manage initiatives registered in
`secrets.newly_created`, according to the `KEEP_INITIATIVES_*` options.

RDB cleanup runs in `after_scenario`, even if the scenario fails.
`after_all` retries only resources whose cleanup failed. Tracking is held only in
memory, in the scenario context: there are no state files or recovery from interrupted runs.

- CSV files, reports, upload records, and products are deleted only for files created
  by the run, identified by organization, initiative, and exact filename. Before a
  write, checks ensure that the GTINs do not belong to pre-existing products.
- Imports, reimports, and email updates use dedicated producers generated per
  scenario: associations are tracked by ID and then deleted. The current state
  is read only at deletion, as required by the backend's CAS contract. Writes to
  associations of producers not created by the scenario are blocked before the
  request: restoration snapshots are unnecessary.
- Only consent records belonging to newly generated test users and portal initiatives
  whose IDs come from confirmed creations in the run are removed.

The backend must expose the internal `/idpay/register/clean/fixtures` APIs with
`TEST_SUPPORT_ENABLED=true`, as in `idpay-transactions`. The application property
is `app.test-support.enabled`, defaulting to `false`. DEV/UAT Helm values enable
the flag; production remains disabled by default. The endpoints do not require
a dedicated token. The suite checks API availability before the RDB scenarios.
The cleanup controller is excluded from Swagger documentation and uses only
the internal ingress: no APIM routes or Terraform changes are added.

Cleanup waits up to 120 seconds for uploads still being processed and asynchronous
portal deletions; the limit is defined in code. Incomplete cleanup produces an error
in the scenario hook without deleting associations linked to uploads that remain.
Dry runs do not invoke these APIs.

Verification on 9 October: 27 unit tests passed; the full UAT suite had 95 passing
scenarios and 1 concurrency failure. Cleanup succeeded for all 96 scenarios and
for the isolated rerun of the failed case. See the report above for details.

## Datasets

`asset_register.datasets` contains optional overrides using the names referenced
by the features. `profile` selects the profile and `initiative` selects alias A/B.
For tests that write data, expectations derive from inputs or confirmed writes.

The suite prepares CSV files, products, history, reports, associations, and draft
initiatives through APIs. Four product/batch read tests reuse existing data:
products must exist for the configured producer and another organization in A,
as well as products in B. They verify consistency and isolation, rather than
independently establishing inventory completeness.
SelfCare cases require an existing institution with a known VAT number.

Following the standup decision, the cases for renewed acceptance after a version
change and for a disabled producer association were removed from the Behave suite.
Coverage remains in backend JUnit tests; future UAT integration is deferred,
without developing dedicated test APIs now. These cases are not counted as passed
or skipped. Details are in the [decision document](rdb-team-discussion.md).
Historical reports retain the original scope of 98 scenarios.

Concurrent upload tests prepare a 100-row EPREL CSV and verify that it is active
before and after the second upload. Preliminary cleanup checks for both files
run before the first upload, outside the measured window.
These tests do not require `datasets.upload in progress`.
The producer must be enabled on A/B and have no other active uploads; the test
waits for its own CSV to finish without suspending shared consumers.

## Functional scope

The `/register/token/test` signer generates application JWTs; it is not a real
SelfCare exchange. The expired-token test requires the policy to honor `exp`,
or an already expired signed JWT in `application_tokens.expired`.

The EPREL conditions product not found/not published/blocked and organization/brand
not verified are outside the agreed scope and are not counted as passed.
Category, valid/mixed processing, and minimum energy class remain in scope:

| Category | Minimum |
| --- | --- |
| WASHINGMACHINES, WASHERDRIERS, OVENS | A |
| RANGEHOODS | B |
| DISHWASHERS, TUMBLEDRYERS | C |
| REFRIGERATINGAPPL | D |
| COOKINGHOBS | No EPREL check |

All use `Codice GTIN/EAN`. EPREL categories use the EPREL_STANDARD template.
Public fixtures are in `conf/rdb/eprel.json`, with overrides through `asset_register.eprel`.
The portal supports downloading the error report, not the original CSV from upload history.

The two scenarios that force email/OneTrust unavailability are excluded from the suite.
Resilience with simulated dependencies should be verified in backend tests.

## Email and reports

The three email tests invoke the service directly and require **HTTP 204 with an
empty body**. `templateValues.portalUrl` derives from `TARGET_ENV` and the
`RDB_EMAIL_PORTAL_URLS` map in `settings.yaml`, with dev/UAT URLs. A missing entry
blocks sending. The service builds the HTML from templates; the test does not
certify mailbox delivery or the automatic RDB backend trigger.

The payload is printed with the recipient masked and without a token. On failure,
the assertion includes `code` and `message`. With JUnit, stdout is included in the
XML files; without JUnit, `--no-capture` displays it in the console.

`tests/reports/` contains generated results, ignored by Git and removable when
no longer needed. JUnit is the XML results format, not a separate suite.
The `tests/test_*.py` files belong to the pytest suite and are not reports.

## TD-RDB-001

Validation of a CSV larger than 2 MB temporarily tolerates HTTP 500 only in the
`@rdb_td_001` case. The correct result is HTTP 200, `status: KO`,
`errorKey: product.invalid.file.maxsize`. Passing with HTTP 500 does not certify
the backend fix. Remove the tolerance and tag after verifying the fix in the
selected environment.
