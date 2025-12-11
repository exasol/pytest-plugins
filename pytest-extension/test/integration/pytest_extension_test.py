from textwrap import dedent

import pytest
from exasol.pytest_backend import (
    BACKEND_ALL,
    BACKEND_OPTION,
)

pytest_plugins = ["pytester"]


def test_extension_all_backends(pytester):
    test_code = dedent(
        r"""
        import json
        import pytest
        import click
        from click.testing import CliRunner
        import exasol.bucketfs as bfs
        from exasol.python_extension_common.connections.pyexasol_connection import open_pyexasol_connection
        from exasol.python_extension_common.connections.bucketfs_location import create_bucketfs_location
        from exasol.python_extension_common.cli.std_options import (StdParams, StdTags, select_std_options)
        from exasol.pytest_backend import (BACKEND_ONPREM, BACKEND_SAAS)

        TEST_SCHEMA = 'PYTEXT_TEST_SCHEMA'
        TEST_FILE_CONTENT = b'Gravity Sucks'

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
            bfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path=path_in_bucket)
            bfs_path.write(TEST_FILE_CONTENT)

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
            file_content = b"".join(bfs_path.read())

            assert file_content == TEST_FILE_CONTENT

        def validate_database_std_params(**kwargs):
            with open_pyexasol_connection(**kwargs) as conn:
                res = conn.execute('SELECT SESSION_ID FROM SYS.EXA_ALL_SESSIONS;').fetchall()
                assert res

        def validate_bucketfs_std_params(**kwargs):
            # Temporary work around for the bug in PEC (Issue#78 - no default for the path_in_bucket
            if StdParams.path_in_bucket.name in kwargs and kwargs[StdParams.path_in_bucket.name] is None:
                kwargs[StdParams.path_in_bucket.name] = ''
            bfs_path = create_bucketfs_location(**kwargs)
            bfs_path = bfs_path / 'test_file.txt'
            bfs_path.write(TEST_FILE_CONTENT)
            file_content = b"".join(bfs_path.read())
            assert file_content == TEST_FILE_CONTENT

        def validate_cli_args(backend, cli_args, base_tag, callback):
            if backend == BACKEND_ONPREM:
                tags = base_tag | StdTags.ONPREM
            elif backend == BACKEND_SAAS:
                tags = base_tag | StdTags.SAAS
            else:
                ValueError(f'Unknown backend {backend}')
            opts = select_std_options(tags)
            cmd = click.Command('whatever', params=opts, callback=callback)
            runner = CliRunner()
            runner.invoke(cmd, args=cli_args, catch_exceptions=False)

        def test_database_std_params(database_std_params):
            validate_database_std_params(**database_std_params)

        def test_bucketfs_std_params(bucketfs_std_params):
            validate_bucketfs_std_params(**bucketfs_std_params, path_in_bucket='test_bucketfs_std_params')

        def test_database_cli_args(backend, database_cli_args):
            validate_cli_args(backend, database_cli_args, StdTags.DB, validate_database_std_params)

        def test_bucketfs_cli_args(backend, bucketfs_cli_args):
            validate_cli_args(backend, bucketfs_cli_args, StdTags.BFS, validate_bucketfs_std_params)       
    """
    )
    pytester.makepyfile(test_code)
    result = pytester.runpytest("-s", BACKEND_OPTION, BACKEND_ALL)
    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=12, skipped=0)
