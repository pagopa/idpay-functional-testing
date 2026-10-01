# IDPay Functional Testing

Repository containing BDD and functional tests for the PARI platform.

## Reports and documentation

- GitHub Pages (docs + report): https://pagopa.github.io/idpay-functional-testing/docs
- Public Allure reports are published from `uat` runs only.
- RDB features, environment datasets and reusable utilities: [RDB BDD tests](docs/rdb.md).

## Test execution

Test execution is managed **only through GitHub Actions**.

Main workflow: `.github/workflows/test-run.yaml`

Manual execution:
1. Go to **Actions** in the repository.
2. Select the **test-run** workflow.
3. Click **Run workflow**.
4. Set the parameters:
   - `environment`: `uat`
   - `test_type`: `bdd`
   - `feature`: BDD tag to run (`rdb` for all RDB scenarios)
5. Start the run.

### Environment and secrets

Features run against the deployed environment selected by `PARI_TARGET_ENV`.
`PARI_SECRET_PATH` points to its `pari-feature-secrets.json`; the workflow retrieves
this file from Key Vault. The default path for configuration is
`conf/pari-feature-secrets.json`. Never commit the secrets file.

The runner executes Behave with the selected tag, for example:

```console
pipenv run behave --junit --junit-directory "tests/reports/behave" --tags @rdb
```

This command calls the environment APIs and requires the corresponding secrets.
Dataset requirements and dependency observation are described in
[RDB BDD tests](docs/rdb.md).

### Dependency setup (pipenv)

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
