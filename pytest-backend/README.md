# pytest-exasol-backend Plugin

The `pytest-exasol-backend` plugin is a collection of pytest fixtures commonly used for testing
projects related to Exasol. In particular, it provides unified access to both Exasol On-Prem and
SaaS backends. This eliminates the need to build different sets of tests for different backends.

## Features

* Provides session level fixtures that can be turned into connection factories for the database and the BucketFS.
* Automatically makes the tests running on the selected backends.
* Allows selecting either or both backends from the CLI that executes the pytest.
* Starts the selected backends preemptively and in parallel.

## Installation

The pytest-exasol-backend plugin can be installed using pip:

```shell
pip install pytest-exasol-backend
```

## Usage in Tests

Below is an example of a test that requires access to the database. Note, that by default
this test will run twice - once for each backend.

```python
import pyexasol

def test_number_of_rows_in_my_table(backend_aware_database_params):
    with pyexasol.connect(**backend_aware_database_params, schema='MY_SCHEMA') as conn:
        num_of_rows = conn.execute('SELECT COUNT(*) FROM MY_TABLE;').fetchval()
        assert num_of_rows == 5
```

Here is an example of a test that requires access to the BucketFS. Again, this test will
run for each backend, unless one of them is disabled in the CLI.

```python
import exasol.bucketfs as bfs

def test_my_file_exists(backend_aware_bucketfs_params):
    my_bfs_dir = bfs.path.build_path(**backend_aware_bucketfs_params, path='MY_BFS_PATH')
    my_bfs_file = my_bfs_dir / 'my_file.dat'
    assert my_bfs_file.exists()
```

Sometimes it may be necessary to know which backend the test is running with. In such
a case the `backend` fixture can be used, as in the example below.

```python
def test_something_backend_sensitive(backend):
    if backend == 'onprem':
        # Do something special for the On-Prem database.
        pass
    elif backend == 'saas':
        # Do something special for the SaaS database.
        pass
    else:
        raise RuntimeError(f'Unknown backend {backend}')
```

## Selecting Backends in CLI

By default, none of the backends is selected for testing. Please use the `--backend` option to specify the target backend.
The command below runs the tests on an on-prem database.

```shell
pytest --backend=onprem my_test_suite.py
```

This following command runs the test on two backends.

```shell
pytest --backend=onprem --backend=saas my_test_suite.py
```

The next command runs the test on all backends, which currently is equivalent to the previous command since there
are only two backends available.

```shell
pytest --backend=all my_test_suite.py
```

Please note that all selected backends starts preemptively, regardless of their actual usage in tests.
Therefore, it is important to make sure the backends are not selected where they are not needed,
for instance when running unit tests only.

## Setting ITDE parameters in CLI

Sometimes the default ITDE parameters cannot satisfy the test requirements. The plugin allows setting
some of the parameters of the [api.spawn_test_environment(...)](https://github.com/exasol/integration-test-docker-environment/blob/92cc67b8f9ab78c52106c1c4ba19fe64811bcb2c/exasol_integration_test_docker_environment/lib/api/spawn_test_environment.py#L35)
function. The parameter values can be provided in the CLI options. Currently, it is possible to set values of the following parameters:
 - `--itde-db-mem-size`
 - `--itde-db-disk-size`
 - `--itde-nameserver`
 - `--itde-db-version`

In the example below the tests are run using an instance of the DockerDB with increased memory.

```shell
pytest --backend=onprem --itde-db-mem-size "8 GiB" my_test_suite.py
```

These options are ignored if the "onprem" backend is not selected.
