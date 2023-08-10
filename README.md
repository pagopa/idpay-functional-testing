# IDPay Functional Testing

## Installation

Clone the repository:

```commandline
git clone https://github.com/pagopa/idpay-functional-testing.git
```

Enter the cloned repository:

```commandline
cd idpay-functional-testing
```

Install [pipenv](https://pipenv.pypa.io/en/latest/):

```
pip install pipenv
```

Create and enter the virtual environment:

```commandline
pipenv shell
```

Install dependencies:

```commandline
pipenv sync
```

### Create `.secret.yaml` based on `.secrets_semplate.yaml` and customize it.

## Usage

Run tests with Behave:

```commandline
[IDPAY_TARGET_ENV=<myenv>] behave --junit --junit-directory "tests/reports/behave"
```

> Default target environment is **dev**.

For example this command runs verbose all API test and save the junitxml report to a file:

```commandline
pytest --junitxml=tests/reports/junit.xml -vv -m "API"
```

Run tests with PyTest:

```commandline
[IDPAY_TARGET_ENV=<myenv>] pytest [--junitxml=path/to/report.xml] [-vv] [-m "[not] <TEST_MARKER>"]
```

> Default target environment is **dev**.

For example this command runs verbose all API test and save the junitxml report to a file:

```commandline
pytest --junitxml=tests/reports/junit.xml -vv -m "API"
```
