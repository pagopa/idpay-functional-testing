# IDPay Functional Testing

Repository containing BDD and functional tests for the PARI platform.

## Reports and documentation

- GitHub Pages (docs + report): https://pagopa.github.io/idpay-functional-testing/docs
- Public Allure reports are published from `uat` runs only. The `/bdd/` report shows
  the latest published run, including tag-filtered runs; it is not a cumulative
  history of every local or CI execution. Check the selected tag in the linked
  Actions run before comparing totals.
- UI Playwright report is published from `uat` runs to `https://pagopa.github.io/idpay-functional-testing/ui`.
- CI runs with `feature=all` execute the two Bonus selections. Scenarios without
  either Bonus tag are outside that matrix. Local runs do not update GitHub Pages
  automatically.
- RDB features, environment datasets and reusable utilities: [RDB BDD tests](docs/rdb.md).
- Family coverage for Elettrodomestici and Decoder: [Family BDD tests](docs/family.md).

## Test execution

Remote integration test execution is managed through GitHub Actions.

Main workflow: `.github/workflows/test-run.yaml`

Manual execution:
1. Go to **Actions** in the repository.
2. Select the **test-run** workflow.
3. Click **Run workflow**.
4. Set the parameters:
   - `environment`: `uat`
   - `test_type`: `bdd`
   - `feature`: BDD tag to run
   - `reward_batch_cleanup`: Cleanup environment after test run
5. Start the run.

### Environment and secrets

Features run against the deployed environment selected by `PARI_TARGET_ENV`.
`PARI_SECRET_PATH` points to its `pari-feature-secrets.json`; the workflow retrieves
this file from Key Vault. The default path for configuration is
`conf/pari-feature-secrets.json`. Never commit the secrets file.

### BDD initiative configuration

The Bonus features use `INITIATIVE_CONFIGS` in `bdd/environment.py` for initiative
names and default product GTINs. Configuration is selected from execution inputs,
not from feature or scenario tags. `PARI_FEATURE_INITIATIVE` is the only source
for selecting the initiative; it must be one concrete initiative name. The
manual workflow defaults its initiative input to `all` and expands that into
separate runs for each initiative. Behave tags, including `--tags`, only filter
which features and scenarios run; they do not choose an initiative.

Feature tags still control Behave filtering: a shared feature can carry both
`@bonus_elettrodomestici` and `@bonus_decoder`, without selecting two configurations
or provisioning both initiatives. The pipeline matrix supplies a concrete
`PARI_FEATURE_INITIATIVE` for each run. For local execution, set both the
initiative and any desired filter, for example
`PARI_FEATURE_INITIATIVE=bonus_decoder pipenv run behave bdd/features/bonus_decoder --tags bonus_decoder`.

`Given the initiative is active` resolves the logical initiative name to its
deployed ID, provisions it if needed, and initializes scenario state. Generic
onboarding steps use `context.initiative_id`; barcode steps with
`default product GTIN` use `context.product_gtin`. Newly provisioned initiatives
remain covered by cleanup and failure-preservation controls. Product-specific steps remain available where used by active scenarios.
`Scenario Outline` / `Examples` remain appropriate for business inputs such as
operator roles, family members and invalid RDB data, not environment configuration.

The runner executes Behave with the selected tag, for example:

### Commands

```commandline
PARI_FEATURE_INITIATIVE=<initiative> [PARI_TARGET_ENV=<myenv>] behave [--junit --junit-directory <JUNIT_OUTPUT_DIR>] [--tags @<[TEST_TAG/s]>]
```

For example, run the active onboarding scenarios in UAT and save JUnit XML:

```commandline
PARI_FEATURE_INITIATIVE=bonus_elettrodomestici behave --junit --junit-directory "tests/reports/behave" --tags @onboarding
```

### Local environment commands (pipenv)

Install pipenv:

```bash
pip install pipenv
```

Install project dependencies:

```bash
pipenv sync
```

Activate the virtual environment shell:

```bash
pipenv shell
```

Deactivate the shell:

```bash
exit
```

### Active suites and offline checks

The maintained BDD suites are `common_bonus_features`, `bonus_elettrodomestici`
and `bonus_decoder`. Historical cashback, whitelist, IDPay-code and discount-type
suites and the disabled pytest integration workflow were retired. The `ranking`
and `ranking_family` suites are preserved in [the ranking archive](archive/ranking/README.md)
for possible Bonus Valore reuse; they are not part of the active BDD suite.
`tests/unit` contains the active RDB cleanup tests, which mock HTTP operations.

Offline checks use placeholder configuration and make no remote requests:

```bash
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run python -m unittest discover -s tests/unit -v
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' PARI_FEATURE_INITIATIVE=bonus_elettrodomestici pipenv run behave --dry-run
```

For PowerShell, set `$env:PARI_SECRET_PATH` and `$env:PARI_TARGET_ENV` before
running the commands. The template is for offline checks only; real BDD runs
require environment credentials from Key Vault and connectivity to dev/uat.

Documentation build (install `mkdocs-material` as in the docs workflow):

```bash
python scenario_parser.py --page-name "PARI Functional Testing" --repo-name idpay-functional-testing --root-dir bdd/features
mkdocs build --strict
```

Pull requests and merge groups invoke the main workflow; remote BDD execution
is skipped on pull requests. Manual runs select the environment and feature tag.

## UI test execution (Playwright)

The repository includes a Playwright setup under `tests/ui`.

### Local setup

```bash
npm ci
npx playwright install chromium
```

### Local run

```bash
npm run ui:test
```

To run against a deployed environment, set `UI_BASE_URL`:

```bash
UI_BASE_URL='https://<your-ui-host>' npm run ui:test
```

For PowerShell:

```powershell
$env:UI_BASE_URL='https://<your-ui-host>'
npm run ui:test
```

### Authenticated UI tests

The Playwright authenticated fixture is in `tests/ui/fixtures/auth.fixture.ts` and stores
the session in `playwright/.auth/user.json`.

Required variables for authenticated tests:

- `UI_BASE_URL`
- `USER_USERNAME`
- `USER_PASSWORD`

Optional UI selector overrides (when defaults do not match the target app):

- `UI_LOGIN_PATH` (default: `/accesso`)
- `UI_LOGIN_BUTTON_TESTID` (default: `logInButton`)
- `UI_SPID_BUTTON_TESTID` (default: `spidButton`)
- `UI_IDP_BUTTON_TESTID` (default: `idp-button-https://idp.uat.oneid.pagopa.it`)
- `UI_USERNAME_LABEL` (default: `Username`)
- `UI_PASSWORD_LABEL` (default: `Password`)
- `UI_SUBMIT_BUTTON_NAME` (default: `Accedi`)
- `UI_CONSENT_BUTTON_NAME` (default: `Do il consenso`)
- `UI_POST_LOGIN_PATH` (optional post-login URL assertion)

PowerShell example:

```powershell
$env:UI_BASE_URL='https://<your-ui-host>'
$env:USER_USERNAME='<your-username>'
$env:USER_PASSWORD='<your-password>'
npm run ui:test
```

### CI/CD integration

- Main workflow: `.github/workflows/test-run.yaml`
- Reusable UI workflow: `.github/workflows/test-run-ui.yaml`
- Manual dispatch `test_type` options:
  - `bdd`
  - `ui`
  - `all`

The UI workflow uploads `test-results` and `playwright-report` as artifacts.
On pull requests, the report is available as Action artifact (`ui-test-results`).
The workflow also posts a PR comment with a direct preview artifact link.
On `main`, the HTML report is published to GitHub Pages under `/reports/<run_id>/`.