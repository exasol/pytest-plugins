from textwrap import dedent
import re
import pytest

import pyexasol
import exasol.bucketfs as bfs

pytest_plugins = ["pytester"]


@pytest.mark.parametrize(
    "test_case,cli_args,num_passed,num_skipped",
    [
        (
            dedent("""
                def test_onprem_only(backend, use_onprem, use_saas):
                    assert backend == 'onprem'
                    assert use_onprem
                    assert not use_saas
            """),
            ["--backend", "onprem"],
            1, 1
        ),
        (
            dedent("""
                def test_saas_only(backend, use_onprem, use_saas):
                    assert backend == 'saas'
                    assert not use_onprem
                    assert use_saas
            """),
            ["--backend", "saas"],
            1, 1
        ),
        (
            dedent("""
                def test_default(backend, use_onprem, use_saas):
                    assert use_onprem
                    assert use_saas
                """),
            [],
            2, 0
        ),
        (
            dedent("""
                def test_no_backend(use_onprem, use_saas):
                    assert use_onprem
                    assert use_saas
                """),
            [],
            1, 0
        ),
    ], ids=["onprem_only", "saas_only", "default", "no_backend"])
def test_pass_options_via_cli(pytester, test_case, cli_args, num_passed, num_skipped):
    """
    This test could also be called a unit test and verifies that the CLI
    arguments are registered correctly, can be passed to pytest, and are
    accessible within external test cases.
    """
    pytester.makepyfile(test_case)
    result = pytester.runpytest(*cli_args)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=num_passed, skipped=num_skipped)


def test_backend_aware_database_params(backend_aware_database_params):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res


def test_backend_aware_bucketfs_params(backend_aware_bucketfs_params):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
