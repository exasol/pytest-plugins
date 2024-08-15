# pytest-exasol-slc Plugin

The `pytest-exasol-slc` plugin provides a pytest fixture for uploading a script language container
into the database. The fixture is backend agnostic. It runs for the selected backends
(see the documentation for the `pytest-exasol-backend` plugin).

## Installation

The pytest-exasol-slc plugin can be installed using pip:

```shell
pip install pytest-exasol-slc
```

## Usage in Tests

Below is an example of a test that requires a script language container to be uploaded into the database.
Note, that by default this test will run twice - once for each backend.

```python
import pyexasol

def test_something_with_slc(upload_slc, container_file_path, language_alias):

    upload_slc(container_file_path=container_file_path, language_alias=language_alias)

    # Now run the actual test
```
