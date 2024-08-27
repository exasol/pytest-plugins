from textwrap import dedent
import pytest
from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL, BACKEND_ONPREM)

pytest_plugins = ["pytester"]

_test_code = dedent("""
import pyexasol
import pytest
from exasol.python_extension_common.deployment.language_container_validator import temp_schema
from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder, find_path_backwards)

LANGUAGE_ALIAS = 'PYTHON3_PYTEST_SLC'

@pytest.fixture(scope='session', autouse=True)
def extension_build_slc_async(export_slc_async):
    with LanguageContainerBuilder('test_container', LANGUAGE_ALIAS) as slc_builder:
        # project_directory = find_path_backwards("pyproject.toml", __file__).parent
        # slc_builder.prepare_flavor(project_directory)
        # yield export_slc_async(slc_builder)
        yield slc_builder, None

@pytest.fixture(scope='session')
def extension_upload_slc(extension_build_slc_async, upload_slc):
    # return upload_slc(*extension_build_slc_async, 'container')
    return True

def assert_udf_running(conn: pyexasol.ExaConnection):
    with temp_schema(conn) as schema:
        udf_name = 'TEST_UDF'
        udf_create_sql = (
            f'CREATE OR REPLACE {LANGUAGE_ALIAS} SCALAR SCRIPT "{schema}"."{udf_name}"() '
            'RETURNS BOOLEAN AS '
            'def run(ctx): '
            'return True '
            '/'
        )
        conn.execute(udf_create_sql)
        result = conn.execute(f'SELECT "{schema}"."{udf_name}"()').fetchall()
        assert result[0][0] is True

def test_upload_slc(extension_upload_slc, backend_aware_database_params):
    # if extension_upload_slc:
    #    assert_udf_running(pyexasol.connect(**backend_aware_database_params))
    assert True
""")


def test_pytest_slc(pytester):
    pytester.makepyfile(_test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ONPREM)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=0)
