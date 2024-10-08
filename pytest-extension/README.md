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

The following fixtures are used to test various deployment scenarios where the connection parameters
for the Database and the BucketFS are supplied in a command line. The first two fixtures provide dictionaries
of standard cli parameters (`StdParams`) defined in the `exasol-python-extension-common`.

    `database_std_params` - the Database connection parameters.
    `bucketfs_std_params` - the BucketFs connection parameters.

The next two fixtures - `database_cli_args` and `bucketfs_cli_args` - give the same parameters as the previous two
but in the form of command line arguments. They are helpful for testing the CLI directly, for example using the
click.CliRunner as in the samples below. There is also a fixture - `cli_args` - that combines these two argument
strings.

```python
import click
from click.testing import CliRunner
from exasol.python_extension_common.cli.std_options import (StdParams, StdTags, select_std_options)
from exasol.pytest_backend import (BACKEND_ONPREM, BACKEND_SAAS)

def test_db_connection_cli(backend, database_cli_args):
    if backend == BACKEND_ONPREM:
        tags = StdTags.DB | StdTags.ONPREM
    elif backend == BACKEND_SAAS:
        tags = StdTags.DB | StdTags.SAAS
    else:
        ValueError(f'Unknown backend {backend}')

    def test_something_with_db(**kwargs):
        pass

    opts = select_std_options(tags)
    cmd = click.Command('whatever', params=opts, callback=test_something_with_db)
    runner = CliRunner()
    runner.invoke(cmd, args=database_cli_args, catch_exceptions=False, standalone_mode=False)

def test_bucketfs_connection_cli(backend, bucketfs_cli_args):
    if backend == BACKEND_ONPREM:
        tags = StdTags.BFS | StdTags.ONPREM
    elif backend == BACKEND_SAAS:
        tags = StdTags.BFS | StdTags.SAAS
    else:
        ValueError(f'Unknown backend {backend}')

    def test_something_with_bucketfs(**kwargs):
        pass

    opts = select_std_options(tags)
    cmd = click.Command('whatever', params=opts, callback=test_something_with_bucketfs)
    runner = CliRunner()
    runner.invoke(cmd, args=bucketfs_cli_args, catch_exceptions=False, standalone_mode=False)
```

Note, that by default the tests will run twice - once for each backend.
