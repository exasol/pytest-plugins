from textwrap import dedent
import pytest
from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL)

pytest_plugins = ["pytester"]

MAIN_LANGUAGE_ALIAS = 'PYTHON3_PYTEST_SLC'
ALT_LANGUAGE_ALIAS = 'PYTHON3_PYTEST_SLC_ALT'

_test_code = dedent(fr"""
import pyexasol
import pytest
from exasol.python_extension_common.deployment.language_container_validator import temp_schema
from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder, find_path_backwards)

@pytest.fixture(scope='session')
def slc_builder() -> LanguageContainerBuilder:
    with LanguageContainerBuilder('test_container') as container_builder:
        project_directory = find_path_backwards("pyproject.toml", "{__file__}").parent
        container_builder.prepare_flavor(project_directory)
        yield container_builder

@pytest.fixture(scope='session')
def language_alias() -> str:
    return "{MAIN_LANGUAGE_ALIAS}"

def assert_udf_running(conn: pyexasol.ExaConnection, lang_alias: str) -> None:
    with temp_schema(conn) as schema:
        udf_name = 'TEST_UDF'
        udf_create_sql = (
            f'CREATE OR REPLACE {{lang_alias}} SCALAR SCRIPT "{{schema}}"."{{udf_name}}"() '
            'RETURNS BOOLEAN AS '
            'def run(ctx): '
            'return True '
            '\n/'
        )
        conn.execute(udf_create_sql)
        result = conn.execute(f'SELECT "{{schema}}"."{{udf_name}}"()').fetchall()
        assert result[0][0] is True

def test_deploy_slc(deploy_slc, deployed_slc, backend_aware_database_params):
    # We will activate the SLC also with an alternative alias and check that both
    # the main and the alternative alias work.
    deploy_slc("{ALT_LANGUAGE_ALIAS}")
    for lang_alias in ["{MAIN_LANGUAGE_ALIAS}", "{ALT_LANGUAGE_ALIAS}"]:
        assert_udf_running(pyexasol.connect(**backend_aware_database_params), lang_alias)
""")


def test_pytest_slc(pytester):
    pytester.makepyfile(_test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ALL)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=0)
