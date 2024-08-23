from textwrap import dedent
import pytest
from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL)

pytest_plugins = ["pytester"]

_test_code = dedent(f"""
import pyexasol
import pytest
from exasol.python_extension_common.deployment.language_container_validator import temp_schema
from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder, find_path_backwards)

LANGUAGE_ALIAS = 'PYTHON3_PYTEST_SLC'

@pytest.fixture(scope='session', autouse=True)
def extension_build_slc_async(export_slc_async):
    with LanguageContainerBuilder('test_container', LANGUAGE_ALIAS) as slc_builder:
        project_directory = find_path_backwards("pyproject.toml", __file__).parent
        slc_builder.prepare_flavor(project_directory)
        yield export_slc_async(slc_builder)

@pytest.fixture(scope='session')
def extension_upload_slc(extension_build_slc_async, upload_slc):
    upload_slc(*extension_build_slc_async, 'container')

def test_upload_slc(extension_upload_slc, backend_aware_database_params):
    assert True
""")


def test_pytest_slc(pytester):
    pytester.makepyfile(_test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ALL)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=0)
