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

Create a virtual environment:

```commandline
python -m venv venv
```

Enter the virtual environment:

```commandline
source venv/bin/activate
```

Install dependencies:pip

```commandline
pip install -r requirements.txt
```

### Create `.secret.yaml` based on `.secrets_semplate.yaml` and customize it.

## Usage

Run tests:

```commandline
[IDPAY_TARGET_ENV=<myenv>] pytest [--junitxml=path/to/report.xml] [-vv] [-m "[not] <TEST_MARKER>"]
```

> Default target environment is **dev**.

For example this command runs verbose all API test and save the junitxml report to a file:

```commandline
pytest --junitxml=tests/reports/junit.xml -vv -m "API"
```

## Available initiatives:

- `not_started` : initiative that is not started yet.
