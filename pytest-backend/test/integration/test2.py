import pytest

import pyexasol
import exasol.bucketfs as bfs


@pytest.mark.skip
def test_backend_aware_database_params11(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.skip
def test_backend_aware_database_params12(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.skip
def test_backend_aware_database_params13(backend_aware_database_params, global_itde_calls, global_saas_calls):
    conn = pyexasol.connect(**backend_aware_database_params)
    res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
    assert res
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.skip
def test_backend_aware_bucketfs_params11(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test1')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.skip
def test_backend_aware_bucketfs_params12(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test2')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0


@pytest.mark.skip
def test_backend_aware_bucketfs_params13(backend_aware_bucketfs_params, global_itde_calls, global_saas_calls):
    bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path='plugin_test3')
    file_content = b'In God We Trust'
    bfs_path.write(file_content)
    data_back = b''.join(bfs_path.read())
    bfs_path.rm()
    assert data_back == file_content
    assert global_itde_calls <= 1
    assert global_saas_calls <= 1
    assert global_itde_calls + global_saas_calls > 0
