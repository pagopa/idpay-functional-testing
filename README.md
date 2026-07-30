# IDPay Functional Testing

Repository containing BDD and functional tests for the PARI platform.

## Reports and documentation

- GitHub Pages (docs + report): https://pagopa.github.io/idpay-functional-testing/docs
- Public Allure reports are published from `uat` runs only.

## Test execution

Test execution is managed **only through GitHub Actions**.

Main workflow: `.github/workflows/test-run.yaml`

Manual execution:
1. Go to **Actions** in the repository.
2. Select the **test-run** workflow.
3. Click **Run workflow**.
4. Set the parameters:
   - `environment`: `uat`
   - `test_type`: `all`, `bdd`, `functional`
   - `feature`: BDD tag to run
5. Start the run.

### Commands 

```commandline
[PARI_TARGET_ENV=<myenv>] behave [--junit --junit-directory <JUNIT_OUTPUT_DIR>] [--tags @<[TEST_TAG/s]>]
```

For example this command runs in UAT(default) all onboarding tests and save the junitxml report to a file:

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

Automatic triggers:
- push to `main`
- pull request to `main`
