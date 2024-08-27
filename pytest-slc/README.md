# pytest-exasol-slc Plugin

The `pytest-exasol-slc` plugin provides a pytest fixture for building and uploading a script language container
into the database. The fixture is backend agnostic. It runs for the selected backends
(see the documentation for the `pytest-exasol-backend` plugin).

## Installation

The pytest-exasol-slc plugin can be installed using pip:

```shell
pip install pytest-exasol-slc
```

## Usage in Tests

Below is an example of a test that requires a script language container to be built and uploaded into the database.
Note, that by default this test will run twice - once for each backend.

```python
import pytest

@pytest.fixture(scope='session', autouse=True)
def extension_build_slc_async(export_slc_async, use_onprem, use_saas):
    if use_onprem or use_saas:
        with language_container_factory() as container_builder:
            yield export_slc_async(container_builder)
    else:
        yield None, None

@pytest.fixture(scope='session')
def extension_upload_slc(extension_build_slc_async, upload_slc):
    upload_slc(*extension_build_slc_async)

def test_something_with_slc(extension_upload_slc):
    ...
```
