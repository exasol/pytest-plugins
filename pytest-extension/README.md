# pytest-exasol-extension Plugin

The `pytest-exasol-extension` plugin provides pytest fixtures for preparing a database for the extension tests.
The fixtures are backend agnostic. They run for the selected backends
(see the documentation for the `pytest-exasol-backend` plugin).

## Installation

The pytest-exasol-extension plugin can be installed using pip:

```shell
pip install pytest-exasol-extension
```

## Usage in Tests

Below is an example of a test that requires a database connection with an open test schema.

```python
import pytest

@pytest.fixture(scope="session")
def db_schema_name() -> str:
    """Let's override a randomly generated db schema for the test, giving it a meaningful name."""
    return 'MY_TEST_SCHEMA'

def test_something(pyexasol_connection):
    ...
```

Next, is an example of a test that needs to store a bucket-fs connection object in the database.

```python
def test_something_else(bucketfs_connection_factory):
    bucketfs_connection_factory('my_connection_name,' 'some_path/in_the_bucket')
    ...
```

Note, that by default the tests will run twice - once for each backend.
