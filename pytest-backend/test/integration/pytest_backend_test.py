from textwrap import dedent
import pytest

from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ONPREM, BACKEND_SAAS)

pytest_plugins = ["pytester"]


@pytest.mark.parametrize(
    "test_code",
    [
        dedent("""
            import pyexasol
            def test_backend_aware_database_params(backend_aware_database_params):
                conn = pyexasol.connect(**backend_aware_database_params)
                res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
                assert res
        """),
        dedent("""
            import exasol.bucketfs as bfs
            def test_backend_aware_bucketfs_params(backend_aware_bucketfs_params):
                bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test')
                file_content = b'In God We Trust'
                bfs_path.write(file_content)
                data_back = b''.join(bfs_path.read())
                bfs_path.rm()
                assert data_back == file_content
        """),
    ], ids=["database", "bucketfs"]
)
def test_pytest_backend(pytester, test_code):
    pytester.makepyfile(test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ONPREM, BACKEND_OPTION, BACKEND_SAAS)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=0)
