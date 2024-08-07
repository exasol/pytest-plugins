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


def test_backend_aware_database_params1(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


def test_backend_aware_database_params2(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


def test_backend_aware_database_params3(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


def test_backend_aware_bucketfs_params1(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test1')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


def test_backend_aware_bucketfs_params2(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test2')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


def test_backend_aware_bucketfs_params3(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test3')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.parametrize(
    "test_case,cli_args",
    [
        (
            dedent("""
def test_backend_aware_database_params1(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 1
    assert global_saas_calls == 0

def test_backend_aware_database_params2(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 1
    assert global_saas_calls == 0

def test_backend_aware_database_params3(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 1
    assert global_saas_calls == 0
            """),
            ["--backend", "onprem"]
        ),
        (
            dedent("""
def test_backend_aware_database_params4(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 0
    assert global_saas_calls == 1

def test_backend_aware_database_params5(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 0
    assert global_saas_calls == 1

def test_backend_aware_database_params6(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls == 0
    assert global_saas_calls == 1
            """),
            ["--backend", "saas"]
        )
    ], ids=["onprem_only", "saas_only"])
def test_limited_backend_via_cli(pytester, test_case, cli_args):
    """
    This test could also be called a unit test and verifies that the CLI
    arguments are registered correctly, can be passed to pytest, and are
    accessible within external test cases.
    """
    pytester.makepyfile(test_case)
    result = pytester.runpytest(*cli_args)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=3, skipped=3)
