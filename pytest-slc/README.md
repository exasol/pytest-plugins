# pytest-exasol-slc Plugin

The `pytest-exasol-slc` plugin provides a pytest fixtures for building and uploading a script language container
into the database. The fixtures are backend agnostic. They run for the selected backends
(see the documentation for the `pytest-exasol-backend` plugin).

## Installation

The pytest-exasol-slc plugin can be installed using pip:

```shell
pip install pytest-exasol-slc
```

## Usage in Tests

Below is an example of a test that requires a script language container to be built and deployed in the database.
The example test case overrides two fixtures used internally by the fixture `deployed_slc` in this plugin:
* Fixture `language_alias` provides a meaningful name for the language alias.
* Fixture `slc_builder` prepares the structure of the SLC used in the example test case.

The language container will be activated with value returned by the fixture `language_alias`.
Note, that by default the test will run twice - once for each backend.

```python
import pytest

@pytest.fixture(scope='session')
def language_alias():
    return "MY_LANGUAGE_ALIAS"

@pytest.fixture(scope='session')
def slc_builder(use_onprem, use_saas):
    if use_onprem or use_saas:
        with language_container_factory() as container_builder:
            yield container_builder
    else:
        yield None

def test_something_with_slc(deployed_slc):
    ...
```

Alternatively, the language container can be deployed using the function version of this fixture. The function
can be called multiple times providing an opportunity to activate the language container with different
aliases.

```python
import pytest

@pytest.fixture(scope='session')
def slc_builder(use_onprem, use_saas):
    if use_onprem or use_saas:
        with language_container_factory() as container_builder:
            yield container_builder
    else:
        yield None

def test_something_with_slc(deploy_slc):
    deploy_slc("MY_LANGUAGE_ALIAS")
    ...
```
