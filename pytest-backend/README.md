# pytest-exasol-backend Plugin

The pytest plugin `pytest-exasol-backend` provides pytest fixtures for using various Exasol database instances in integration tests.

In particular, the plugin enables accessing both Exasol On-Prem and SaaS backends in a unified way.

This enables your integration tests to use either backend variant without modification, incl. iterating the test for each backend variant.

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

Alternatively via poetry, recommended as `dev` dependency:

```shell
poetry add pytest-exasol-backend --group dev
```

## Usage in Tests

### PyExasol Connection

This test accesses the database via [PyExasol](github.com/exasol/pyexasol) and requires an additional (`dev`) dependency to `pyexasol` to be added to your project.

Note: If the pytest option `--backend all` is specified, then this test will run **twice** - once for each backend.

```python
import pyexasol

def test_simple_sql(backend_aware_database_params):
    with pyexasol.connect(**backend_aware_database_params) as conn:
        value = conn.execute('SELECT 1 FROM DUAL').fetchval()
        assert value == 1
```

The following test accesses a specific table within a database schema, and requires
* Database schema `MY_SCHEMA` and table `MY_TABLE` to exist
* Database table `MY_TABLE` to contain 5 rows

```python
import pyexasol

def test_number_of_rows_in_my_table(backend_aware_database_params):
    with pyexasol.connect(**backend_aware_database_params, schema='MY_SCHEMA') as conn:
        num_of_rows = conn.execute('SELECT COUNT(*) FROM MY_TABLE;').fetchval()
        assert num_of_rows == 5
```

### BucketFS

This test accesses the [BucketFS](https://docs.exasol.com/db/latest/database_concepts/bucketfs/bucketfs.htm). Again, this test will run for each backend, unless one of them is disabled in the CLI.

```python
import exasol.bucketfs as bfs

def test_my_file_exists(backend_aware_bucketfs_params):
    my_bfs_dir = bfs.path.build_path(**backend_aware_bucketfs_params, path='MY_BFS_PATH')
    my_bfs_file = my_bfs_dir / 'my_file.dat'
    assert my_bfs_file.exists()
```

### Inspect the Selected Backend Variant

For inquiring the currenty selected backend variant in a test case, you can use the `backend` fixture, as shown below.

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

## Selecting Backends on the Command Line

There is no default backend specified for testing.

Please use the `--backend` option to specify the target backend with either `onprem`, `saas`, or `all`.

The plugin automatically starts the selected backends and shuts them down after the test session has finished.
* A SaaS backend is started via [saas-api-python](https://github.com/exasol/saas-api-python/).
* An On-Prem backend via the [ITDE](https://github.com/exasol/integration-test-docker-environment).
* Additionally you can [use an external or local database](#re-using-an-external-or-local-database).

Please noe that all selected backends are started preemptively, regardless of their _actual usage_ in tests.

Therefore, it is important to make sure the backends are not selected where they are not needed, for instance when running unit tests only.

### Example Command Lines

Run the tests on an On-Prem database:

```shell
pytest --backend=onprem my_test_suite.py
```

Run the tests on two backends:

```shell
pytest --backend=onprem --backend=saas my_test_suite.py
```

Run the test on all backends&mdash;equivalent to the previous command:

```shell
pytest --backend=all my_test_suite.py
```

### (Re-)Using an External or Local Database

During development you can shorten the time between code changes and running the tests by (re-)using a backend that is already running.

To save 2-20 minutes each cycle, simply add CLI parameter `--itde-db-version=external`.

Alternatively, you can export environment variable `PYTEST_ADDOPTS`, e.g.
```shell
export PYTEST_ADDOPTS="--backend=onprem --itde-db-version=external"
```

More parameters may be required if your setup deviates from the default values:

| Option                | Default value    |
|-----------------------|------------------|
| `--exasol-host`       | `localhost`      |
| `--exasol-port`       | `8563`           |
| `--exasol-username`   | `sys`            |
| `--exasol-password`   | `exasol`         |
| `--bucketfs-url`      | `127.0.0.1:2580` |
| `--bucketfs-username` | `w`              |
| `--bucketfs-password` | (none)           |

### Setting ITDE Parameters via CLI Options

Sometimes, the default ITDE parameters cannot satisfy the test requirements. The plugin allows setting
some of the parameters of the [api.spawn_test_environment(...)](https://github.com/exasol/integration-test-docker-environment/blob/92cc67b8f9ab78c52106c1c4ba19fe64811bcb2c/exasol_integration_test_docker_environment/lib/api/spawn_test_environment.py#L35)
function. The parameter values can be provided in the CLI options. Currently, it is possible to set values of the following parameters:
 - `--itde-db-mem-size`
 - `--itde-db-disk-size`
 - `--itde-nameserver`
 - `--itde-additional-db-parameter`
 - `--itde-db-version`

This example runs the tests using an instance of the DockerDB with increased memory.

```shell
pytest --backend=onprem --itde-db-mem-size "8 GiB" my_test_suite.py
```

These options are ignored if the "onprem" backend is not selected.

## Naming SaaS instances

For naming SaaS instances, PYTBE defines fixtures `database_name` and `project_short_tag`.

Fixture `database_name`
* Depends on fixture `project_short_tag()` and
* Passes the result to SAPIPY's function `timestamp_name()`, see [SAPIPY user guide](https://github.com/exasol/saas-api-python/blob/main/doc/user_guide/user-guide.md#naming-saas-instances) for more details.

You can override this fixture, but this is not recommended.

Fixture `project_short_tag` tries to read the current project's short tag from the following places
* CLI option `--project-short-tag`
* Environment variable `PROJECT_SHORT_TAG`
* Yaml file `error_code_config.yml`

