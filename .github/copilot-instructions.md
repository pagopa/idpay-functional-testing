# Copilot Instructions

## Project and test execution

This repository is a Python 3.14.6 integration-test suite for the PARI/IDPay platform. It has two complementary suites:

- **BDD:** Gherkin features in `bdd/features/`, implemented by reusable Behave steps in `bdd/steps/`.
- **Functional:** pytest flows in `tests/` that exercise the same remote platform directly.

Tests require access to a configured remote environment, mTLS credentials, API keys, and test identities. Create the ignored local secret file from `conf/pari-feature-secrets-template.json`, or point Dynaconf at a secure alternative with `PARI_SECRET_PATH`. Select its top-level environment section with `PARI_TARGET_ENV` (default: `uat`). Never add a populated secret file, certificate, key, or generated `.pgp` file to Git.

Install dependencies with `pipenv sync`. The GitHub Actions runners additionally install `allure-behave` for BDD and `allure-pytest` for functional tests, so install the applicable package locally before reproducing the CI report command.

```bash
# BDD suite / one feature / one scenario by name
PARI_TARGET_ENV=uat pipenv run behave
PARI_TARGET_ENV=uat pipenv run behave bdd/features/family/onboarding.feature
PARI_TARGET_ENV=uat pipenv run behave bdd/features/bonus_elettrodomestici/onboarding.feature --name "Citizen with no declared ISEE tries to onboard successfully"

# Functional suite / one test / marker selection
PARI_TARGET_ENV=uat pipenv run pytest tests/ -vv
PARI_TARGET_ENV=uat pipenv run pytest tests/test_not_started/test_login_io.py::test_login_io -vv
PARI_TARGET_ENV=uat pipenv run pytest tests/ -m IO -vv

# CI-style reports
PARI_TARGET_ENV=uat pipenv run behave --junit --junit-directory tests/reports/behave --format allure_behave.formatter:AllureFormatter -o allure-results
PARI_TARGET_ENV=uat pipenv run pytest tests/ --alluredir=allure-results-pytest --junitxml=tests/reports/pytest/junit.xml -vv

# Configured checks
pre-commit run --all-files

# Documentation generation, as performed in CI
python3 scenario_parser.py --page-name "PARI Functional Testing" --repo-name idpay-functional-testing --root-dir bdd/features
mkdocs build
```

`pre-commit` is the only configured formatting/lint check; it enforces import order, double-quoted Python strings, and the repository's JSON/YAML/whitespace checks. When changing dependencies, follow the PR template: update `requirements.txt`, `Pipfile`, and `Pipfile.lock` using `pipenv run pip freeze > requirements.txt` and `pipenv install -r requirements.txt`.

## Architecture and lifecycle

`conf/configuration.py` exposes Dynaconf `settings` from `settings.yaml` and environment-specific `secrets`. `settings.yaml` is the source of API paths, timeouts, state constants, and initiative creation payloads; secret JSON supplies base URLs, mTLS material, API keys, and environment-specific IDs.

`api/` is the thin transport layer: functions build URLs from `settings` and `secrets`, set service-specific headers/certificates, apply configured timeouts, and return raw `requests.Response` objects. Put reusable multi-call business flows, polling, fake-data generation, encryption, and assertions in `util/`. Reuse its `retry_*`, onboarding/enrollment, transaction-upload, and cleanup helpers instead of hand-rolled waits or duplicating API sequences.

Both suites create state in the target environment:

- pytest's `conf/conftest.py` creates the `cashback_like`, `not_started`, `complex`, and `timeframes` initiatives before the session, waits for startup, and deletes newly created initiatives at session finish.
- Behave's `bdd/environment.py` creates an initiative once per feature when one of that feature's tags matches a key in `settings.initiatives`, then performs the same cleanup.

Do not introduce parallel test execution unless each worker has isolated initiatives and cleanup. The existing retry helpers account for asynchronous platform state; retain or extend those polling assertions rather than replacing them with fixed sleeps. `KEEP_INITIATIVES_AFTER_TEST` and `KEEP_INITIATIVES_AFTER_FAILED_TEST` are the deliberate debugging controls.

## Test authoring conventions

- Add endpoint-specific request functions to the relevant `api/` module; use configuration values rather than literal hosts, credentials, paths, or timeouts.
- Add a new initiative's payload and expected values under `settings.initiatives`. BDD features that need a provisioned initiative must tag the feature with that exact settings key. Feature steps store scenario state on `context`; initialize it through the existing initiative/setup steps and extend the matching step module.
- Functional tests use domain markers and `@pytest.mark.use_case("<id>")`; preserve these markers when modifying a covered flow so pytest exports the use-case metadata. They share the lifecycle-managed initiative IDs from `secrets.initiatives`.
- Transaction tests generate and PGP-encrypt CSV inputs via `util.transaction_upload`; clean the plaintext and encrypted files with the corresponding utility after use.
- `scenario_parser.py` generates the MkDocs feature pages from `bdd/features/`; generated `docs/index.md` and feature pages are ignored. Change Gherkin sources and step implementations, not generated documentation.
