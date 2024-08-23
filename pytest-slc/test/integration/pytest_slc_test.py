from textwrap import dedent
import pytest
from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL)

pytest_plugins = ["pytester"]

_test_code = dedent("""
import pyexasol
import pytest

def test_upload_slc(backend_aware_database_params):
    print('********** TEST STARTED **************')
    assert True
""")


def test_pytest_slc(pytester):
    pytester.makepyfile(_test_code)
    result = pytester.runpytest('-s', f'{BACKEND_OPTION}={BACKEND_ALL}')
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=0)
