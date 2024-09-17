from textwrap import dedent
import pytest

from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL, BACKEND_ONPREM)
from exasol.pytest_backend.itde import (
    DEFAULT_ITDE_DB_VERSION, DEFAULT_ITDE_DB_MEM_SIZE, DEFAULT_ITDE_DB_DISK_SIZE)

pytest_plugins = ["pytester"]


def test_pytest_all_backends(pytester):
    test_code = dedent("""
        import pyexasol
        import exasol.bucketfs as bfs

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
    """)
    pytester.makepyfile(test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ALL)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=4, skipped=0)


def test_pytest_single_backend(pytester):
    test_code = dedent("""
        import pyexasol

        def test_backend_aware_database_params(backend_aware_database_params):
            conn = pyexasol.connect(**backend_aware_database_params)
            res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
            assert res
    """)
    pytester.makepyfile(test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ONPREM)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1, skipped=1)


def test_itde_options(pytester):
    db_mem_size = '2 TB'
    db_disk_size = '100 TB'
    nameserver1 = 'my_nameserver1'
    nameserver2 = 'my_nameserver2'
    db_version = '1000.100.10.1'

    test_code = dedent(f"""
        def test_backend_aware_database_params(itde_config):
            assert itde_config.db_mem_size == '{db_mem_size}'
            assert itde_config.db_disk_size == '{db_disk_size}'
            assert itde_config.nameserver == ['{nameserver1}', '{nameserver2}']
            assert itde_config.db_version == '{db_version}'
    """)
    pytester.makepyfile(test_code)
    result = pytester.runpytest('--itde-db-mem-size', f"{db_mem_size}",
                                '--itde-db-disk-size', f"{db_disk_size}",
                                '--itde-nameserver', f"{nameserver1}",
                                '--itde-nameserver', f"{nameserver2}",
                                '--itde-db-version', f"{db_version}")
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1)


def test_default_itde_options(itde_config):
    assert itde_config.db_mem_size == DEFAULT_ITDE_DB_MEM_SIZE
    assert itde_config.db_disk_size == DEFAULT_ITDE_DB_DISK_SIZE
    assert itde_config.nameserver == []
    assert itde_config.db_version == DEFAULT_ITDE_DB_VERSION
