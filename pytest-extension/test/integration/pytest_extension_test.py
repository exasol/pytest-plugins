from textwrap import dedent
import pytest

from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ALL)

pytest_plugins = ["pytester"]


def test_extension_all_backends(pytester):
    test_code = dedent(r"""
        import json
        import pytest
        import exasol.bucketfs as bfs

        TEST_SCHEMA = 'PYTEXT_TEST_SCHEMA'

        @pytest.fixture(scope="session")
        def db_schema_name() -> str:
            return TEST_SCHEMA

        def test_pyexasol_connection(pyexasol_connection):
            assert pyexasol_connection.execute(f"SELECT CURRENT_SCHEMA;").fetchval() == TEST_SCHEMA

        def test_bucketfs_connection_factory(bucketfs_connection_factory,                                
                                             pyexasol_connection,
                                             backend_aware_bucketfs_params):
            conn_name = 'test_connection'
            path_in_bucket = 'test_path'
            udf_name = 'EXTRACT_CONNECTION_OBJECT'

            # Write something to the bucket
            file_content = b'Gravity Sucks'
            bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path=path_in_bucket)
            bfs_path.write(file_content)

            # Create a connection object
            bucketfs_connection_factory(conn_name, path_in_bucket)

            # Extract the content of this connection object
            sql = (
                f'CREATE OR REPLACE PYTHON3 SCALAR SCRIPT "{udf_name}"()\n'
                'RETURNS VARCHAR(1024) AS\n'
                'import json\n'
                'def run(ctx):\n'
                f'    conn_obj = exa.get_connection("{conn_name}")\n'
                '    bfs_params = json.loads(conn_obj.address)\n'
                '    bfs_params.update(json.loads(conn_obj.user))\n'
                '    bfs_params.update(json.loads(conn_obj.password))\n'
                '    return json.dumps(bfs_params)\n'
                '/'
            )
            pyexasol_connection.execute(sql)
            sql = f'SELECT "{udf_name}"();'
            bfs_params_str = pyexasol_connection.execute(sql).fetchval()

            # Read from the bucket using data in the connection object
            bfs_params = json.loads(bfs_params_str)
            bfs_path = bfs.path.build_path(**bfs_params)
            file_content_back = b"".join(bfs_path.read())

            assert file_content_back == file_content
    """)
    pytester.makepyfile(test_code)
    result = pytester.runpytest(BACKEND_OPTION, BACKEND_ALL)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=4, skipped=0)
