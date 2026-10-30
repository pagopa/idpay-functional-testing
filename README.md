# IDPay Functional Testing

Repository containing BDD and functional tests for the PARI platform.

## Reports and documentation

- GitHub Pages (docs + report): https://pagopa.github.io/idpay-functional-testing/docs
- Public Allure reports are published from `uat` runs only.
- RDB features, environment datasets and reusable utilities: [RDB BDD tests](docs/rdb.md).

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
not from tags written in the feature or scenario. A single positive initiative
in Behave's `--tags` expression takes precedence; otherwise `PARI_FEATURE_TAG`,
then `FEATURE_TAG` selects the configuration. `all`, an empty value or an unknown
value selects `common_bonus_features` when the CLI does not select an initiative.
Unknown environment values emit a warning. Negated CLI tags do not select an
initiative. If a CLI expression selects multiple initiatives, an environment
variable must disambiguate them or the hook fails explicitly.

Feature tags still control Behave filtering: a shared feature can carry both
`@bonus_elettrodomestici` and `@bonus_decoder`, without selecting two configurations
or provisioning both initiatives. The pipeline matrix supplies `FEATURE_TAG` and
`--tags` for each separate run. For local execution use
`pipenv run behave bdd/features/bonus_elettrodomestici --tags bonus_decoder`.
Setting the environment variable alone does not change Behave's filtering or
validate initiative-specific business rules.

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
[PARI_TARGET_ENV=<myenv>] behave [--junit --junit-directory <JUNIT_OUTPUT_DIR>] [--tags @<[TEST_TAG/s]>]
```

For example, run the active onboarding scenarios in UAT and save JUnit XML:

```commandline
behave --junit --junit-directory "tests/reports/behave" --tags @onboarding
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
and `bonus_decoder`. Historical cashback, ranking, whitelist, IDPay-code and
discount-type suites and the disabled pytest integration workflow were retired.
`tests/unit` contains the active RDB cleanup tests, which mock HTTP operations.

Offline checks use placeholder configuration and make no remote requests:

```bash
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run python -m unittest discover -s tests/unit -v
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run behave --dry-run
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
