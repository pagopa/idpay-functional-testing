# Copilot Instructions

## Project and test execution

This repository is a Python 3.14.6 integration-test suite for the PARI/IDPay platform.
The maintained BDD suites are `bdd/features/common_bonus_features`,
`bdd/features/bonus_elettrodomestici` and `bdd/features/bonus_decoder`, with reusable
Behave steps in `bdd/steps`. `tests/unit` contains offline unittest checks with
mocked HTTP operations. The historical pytest integration suite has been retired. Family coverage for both Bonuses
lives in `bdd/features/common_bonus_features/family`; see `docs/family.md`.
`archive/family` preserves the originals for reference. Current Bonus rules allow
one beneficiary per family; do not restore the historical shared 300-euro budget,
DEMANDED onboarding or QR/IDPay Code flows without a validated business requirement.

`archive/ranking` preserves the historical `ranking` and `ranking_family` scenarios
and dependency references for possible reuse by Bonus Valore. It is not an active
or validated suite. Do not remove this archive as unused code or add it to normal
BDD execution without an explicit decision to reactivate and adapt it.

Install locked dependencies with `pipenv sync`. CI runs BDD through
`.github/workflows/test-run.yaml` and `.github/workflows/test-run-bdd.yaml`.
The remote BDD jobs are skipped on pull requests; manual runs select the environment,
feature tag and reward-batch cleanup option. The `all` matrix runs the two Bonus
configurations and the complementary untagged common selection sequentially.
The public `/bdd/` report always represents the latest published run, including
partial tag selections; inspect the selection in its title and the linked run.
Preserve the JUnit/Allure completeness checks before publication.
CI additionally installs `allure-behave` for its report formatter; it is not needed
for local runs with the default formatter.

Use `conf/pari-feature-secrets-template.json` to prepare an ignored local secret
file, or select a secure file with `PARI_SECRET_PATH`. `PARI_TARGET_ENV` selects its
top-level environment section (default: `uat`). The template contains placeholders
and is only suitable for offline checks. Remote runs need environment connectivity
and credentials; CI retrieves them from Azure Key Vault. Never commit populated
secrets, tokens, certificates, private keys, environment identities or raw reports.

Commands below use Bash environment syntax; in PowerShell set the corresponding
`$env:PARI_SECRET_PATH` and `$env:PARI_TARGET_ENV` before invoking the command.

```bash
# Offline unit tests and active BDD step resolution; no remote requests
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run python -m unittest discover -s tests/unit -v
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run behave --dry-run

# Remote BDD with real, ignored environment configuration
PARI_TARGET_ENV=uat pipenv run behave bdd/features/common_bonus_features bdd/features/bonus_elettrodomestici bdd/features/bonus_decoder --tags bonus_elettrodomestici
PARI_TARGET_ENV=uat pipenv run behave bdd/features/bonus_decoder/onboarding.feature --name "Citizen who has not paid Canone TV tries to onboard unsuccessfully"

# Local JUnit report; add the Allure formatter only when installed
PARI_TARGET_ENV=uat pipenv run behave bdd/features/common_bonus_features bdd/features/bonus_elettrodomestici bdd/features/bonus_decoder --tags bonus_decoder --junit --junit-directory tests/reports/behave

pre-commit run --all-files

# Documentation; install mkdocs-material as in the docs workflow
python scenario_parser.py --page-name "PARI Functional Testing" --repo-name idpay-functional-testing --root-dir bdd/features
mkdocs build --strict
```

The configured pre-commit hooks check Python AST/import order/double-quoted strings,
JSON/YAML/XML, private keys, line endings and whitespace. They can rewrite files;
review their changes. Keep `Pipfile`, `Pipfile.lock` and `requirements.txt` consistent
when changing dependencies; avoid freezing unrelated local tools into runtime requirements.

## Architecture and configuration

`conf/configuration.py` exposes Dynaconf `settings` from `settings.yaml` and
`secrets` from the selected environment. Configuration fails explicitly for a missing
or empty environment. Keep API paths, timeouts, state constants and initiative
payloads in settings; keep URLs, credentials and environment-specific IDs in secrets.

`api/` is the thin HTTP transport layer: build URLs from settings and secrets,
set service-specific headers/certificates and return raw `requests.Response`
objects. Put reusable multi-call flows, polling, data generation and assertions in
`util/`. Reuse existing `retry_*`, onboarding and cleanup helpers rather than
duplicating API sequences or replacing polling with fixed sleeps.

## Initiative selection and lifecycle

Feature and scenario tags filter Behave scenarios. For the Bonus suites, execution
inputs choose the initiative configuration in `bdd/environment.py::INITIATIVE_CONFIGS`:
a single positive Bonus in CLI `--tags` takes precedence, followed by
`PARI_FEATURE_TAG`, then `FEATURE_TAG`. Multiple positive Bonus selections require
an environment variable to disambiguate them. Negated tags do not select an initiative.
With no recognized selection the hook defaults to `bonus_elettrodomestici`.
Shared features may carry both Bonus tags; this does not provision both configurations.

`Given the initiative is active` resolves the logical name to its deployed ID,
creates it when required and initializes scenario state. Generic onboarding steps
use `context.initiative_id`; Barcode steps use `context.product_gtin`. Other feature
tags matching `settings.initiatives` can trigger provisioning in `before_feature`.
When adding a new initiative, update its payload, selection and setup deliberately.

Tests create remote state. `bdd/environment.py` tracks newly created initiatives,
deletes them at the end of the run and coordinates reward-batch cleanup.
`util/rdb_cleanup.py` manages RDB scenario cleanup. Preserve
`KEEP_INITIATIVES_AFTER_TEST`, `KEEP_INITIATIVES_AFTER_FAILED_TEST` and
`PARI_REWARD_BATCH_CLEANUP`, including their failure-preservation semantics.
Do not run tests concurrently against shared initiatives; parallel workers need
isolated initiatives and cleanup. Inspect hook/cleanup failures separately from
business assertions, and do not claim an environment is clean from passing counts alone.

## Test authoring and reports

- Add endpoint-specific requests to the relevant `api/` module; reuse settings and
  secrets instead of literal hosts, credentials, paths or timeouts.
- Keep scenario state on Behave's `context`, initialized by existing setup steps.
  Extend the corresponding step module and reuse utilities before adding duplicates.
- Describe actions with separately asserted outcomes as attempts, for example
  `tries to authorize`, followed by the expected success or rejection assertion.
- Prefer one Given/When/Then flow: group preconditions, actions and outcomes.
  Alternate When/Then blocks only when an intermediate result is a prerequisite.
- Use Scenario Outline/Examples for business inputs such as roles, family members
  and invalid data, rather than selecting deployment configuration.
- Preserve asynchronous polling and meaningful assertions. Do not suppress failures
  or extend timeouts simply to obtain a passing result; diagnose the service state.
- `scenario_parser.py` generates MkDocs pages from active Gherkin. Change feature
  sources and steps, not generated `docs/index.md`, feature pages or `mkdocs.yml`.
  Keep the ranking archive outside the active docs and runner roots.
- Raw JSON/JUnit/Allure logs can contain identities and tokens. Keep them ignored,
  use `util/sanitize-allure-results.py` for published Allure artifacts as CI does,
  and include only sanitized evidence in committed reports.
