from __future__ import annotations
from typing import Any, Callable
import json
import random
import string
import pyexasol
import pytest

from exasol.pytest_backend import BACKEND_ONPREM, BACKEND_SAAS


def _to_json_str(bucketfs_params: dict[str, Any], selected: list[str]) -> str:
    filtered_kwargs = {k: v for k, v in bucketfs_params.items()
                       if (k in selected) and (v is not None)}
    return json.dumps(filtered_kwargs)


def _create_bucketfs_connection(pyexasol_connection: pyexasol.ExaConnection,
                                conn_name: str,
                                conn_to: str,
                                conn_user: str,
                                conn_password: str) -> None:

    query = (f"CREATE OR REPLACE  CONNECTION {conn_name} "
             f"TO '{conn_to}' "
             f"USER '{conn_user}' "
             f"IDENTIFIED BY '{conn_password}'")
    pyexasol_connection.execute(query)


def _create_bucketfs_connection_onprem(pyexasol_connection: pyexasol.ExaConnection,
                                       conn_name: str,
                                       bucketfs_params: dict[str, Any]) -> None:
    conn_to = _to_json_str(bucketfs_params, [
        'backend', 'url', 'service_name', 'bucket_name', 'path', 'verify'])
    conn_user = _to_json_str(bucketfs_params, ['username'])
    conn_password = _to_json_str(bucketfs_params, ['password'])

    _create_bucketfs_connection(pyexasol_connection, conn_name,
                                conn_to, conn_user, conn_password)


def _create_bucketfs_connection_saas(pyexasol_connection: pyexasol.ExaConnection,
                                     conn_name: str,
                                     bucketfs_params: dict[str, Any]) -> None:
    conn_to = _to_json_str(bucketfs_params, ['backend', 'url', 'path'])
    conn_user = _to_json_str(bucketfs_params, ['account_id', 'database_id'])
    conn_password = _to_json_str(bucketfs_params, ['pat'])

    _create_bucketfs_connection(pyexasol_connection, conn_name,
                                conn_to, conn_user, conn_password)


@pytest.fixture(scope="session")
def db_schema_name() -> str:
    """
    The fixture gives a test schema name.
    The user can override this fixture and provide a meaningful name, which can be
    useful when looking at the test results. Otherwise, the schema name will be a
    randomly generated string.
    """
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(12))


@pytest.fixture(scope="session")
def pyexasol_connection(backend_aware_database_params,
                        db_schema_name
                        ) -> pyexasol.ExaConnection:
    """
    The fixture provides a database connection. It opens the test schema,
    creating it if it doesn't exist. In the latter case the schema gets
    deleted and the end of the fixture's life span.
    """
    with pyexasol.connect(**backend_aware_database_params, compression=True) as conn:
        sql = f"SELECT * FROM SYS.EXA_SCHEMAS WHERE SCHEMA_NAME = '{db_schema_name}'"
        use_temp_schema = len(conn.execute(sql).fetchall()) == 0
        if use_temp_schema:
            conn.execute(f'CREATE SCHEMA "{db_schema_name}"')
        conn.execute(f'OPEN SCHEMA "{db_schema_name}"')
        try:
            yield conn
        finally:
            if use_temp_schema:
                conn.execute(f'DROP SCHEMA "{db_schema_name}" CASCADE')


@pytest.fixture(scope='session')
def bucketfs_connection_factory(backend,
                                pyexasol_connection,
                                backend_aware_bucketfs_params
                                ) -> Callable[[str, str | None], None]:
    """
    This is a factory fixture that creates a bucket-fs connection object in a database.
    It takes the following parameters:

    - conn_name:        The name of the connection object.
    - path_in_bucket:   Optional path in the bucket. Bucket root if not specified.

    It will override any existing object with the same name.
    """
    def func(conn_name: str, path_in_bucket: str | None = None) -> None:
        if path_in_bucket:
            bucketfs_params = dict(backend_aware_bucketfs_params)
            bucketfs_params['path'] = path_in_bucket
        else:
            bucketfs_params = backend_aware_bucketfs_params
        if backend == BACKEND_ONPREM:
            _create_bucketfs_connection_onprem(pyexasol_connection, conn_name, bucketfs_params)
        elif backend == BACKEND_SAAS:
            _create_bucketfs_connection_saas(pyexasol_connection, conn_name, bucketfs_params)
        else:
            raise ValueError(f'Unsupported backend {backend}')

    return func
