# pytest-exasol-backend Plugin

The `pytest-exasol-backend` plugin is a collection of pytest fixtures commonly used for testing 
projects related to Exasol. In particular, it provides unified access to both Exasol On-Prem and
SaaS backends. This eliminates the need to build different sets of tests for different backends.

## Features

* Provides session level fixtures that can be turned into connection factories for the database and the BucketFS.
* Automatically makes the tests running on the selected backends.
* Allows selecting either or both backends from the CLI that executes the pytest.

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

# Selecting Backends in CLI

By default, both backends are selected for testing. To run the tests on one backed only, 
the `--backend` option can be used. The command below runs the tests on an on-prem database.

```shell
pytest --backend=onprem my_test_suite.py
```
