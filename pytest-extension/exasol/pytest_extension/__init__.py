from __future__ import annotations

import random
import string
from typing import (
    Any,
    Callable,
)
from urllib.parse import urlparse

import pyexasol
import pytest
from exasol.pytest_backend import (
    BACKEND_ONPREM,
    BACKEND_SAAS,
)
from exasol.python_extension_common.cli.std_options import StdParams
from exasol.python_extension_common.connections.bucketfs_location import (
    create_bucketfs_conn_object_onprem,
    create_bucketfs_conn_object_saas,
)


@pytest.fixture(scope="session")
def db_schema_name() -> str:
    """
    The fixture gives a test schema name.
    The user can override this fixture and provide a meaningful name, which can be
    useful when looking at the test results. Otherwise, the schema name will be a
    randomly generated string.
    """
    return "".join(random.choice(string.ascii_uppercase) for _ in range(12))


@pytest.fixture(scope="session")
def pyexasol_connection(
    backend_aware_database_params, db_schema_name
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


@pytest.fixture(scope="session")
def bucketfs_connection_factory(
    backend, pyexasol_connection, backend_aware_bucketfs_params
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
            bucketfs_params["path"] = path_in_bucket
        else:
            bucketfs_params = backend_aware_bucketfs_params
        if backend == BACKEND_ONPREM:
            create_bucketfs_conn_object_onprem(
                pyexasol_connection, conn_name, bucketfs_params
            )
        elif backend == BACKEND_SAAS:
            create_bucketfs_conn_object_saas(
                pyexasol_connection, conn_name, bucketfs_params
            )
        else:
            raise ValueError(f"Unsupported backend {backend}")

    return func


@pytest.fixture(scope="session")
def onprem_database_std_params(
    use_onprem, backend_aware_onprem_database, exasol_config
) -> dict[str, Any]:
    if use_onprem:
        return {
            StdParams.dsn.name: f"{exasol_config.host}:{exasol_config.port}",
            StdParams.db_user.name: exasol_config.username,
            StdParams.db_password.name: exasol_config.password,
            StdParams.use_ssl_cert_validation.name: False,
        }
    return {}


@pytest.fixture(scope="session")
def onprem_bucketfs_std_params(
    use_onprem, backend_aware_onprem_database, bucketfs_config
) -> dict[str, Any]:
    if use_onprem:
        parsed_url = urlparse(bucketfs_config.url)
        host, port = parsed_url.netloc.split(":")
        return {
            StdParams.bucketfs_host.name: host,
            StdParams.bucketfs_port.name: port,
            StdParams.bucketfs_use_https.name: parsed_url.scheme.lower() == "https",
            StdParams.bucketfs_user.name: bucketfs_config.username,
            StdParams.bucketfs_password.name: bucketfs_config.password,
            StdParams.bucketfs_name.name: "bfsdefault",
            StdParams.bucket.name: "default",
            StdParams.use_ssl_cert_validation.name: False,
        }
    return {}


@pytest.fixture(scope="session")
def saas_std_params(
    use_saas, saas_host, saas_pat, saas_account_id, backend_aware_saas_database_id
) -> dict[str, Any]:
    if use_saas:
        return {
            StdParams.saas_url.name: saas_host,
            StdParams.saas_account_id.name: saas_account_id,
            StdParams.saas_database_id.name: backend_aware_saas_database_id,
            StdParams.saas_token.name: saas_pat,
        }
    return {}


@pytest.fixture(scope="session")
def database_std_params(
    backend, onprem_database_std_params, saas_std_params
) -> dict[str, Any]:
    """
    This is a collection of StdParams parameters required to open a
    database connection for either DockerDB or SaaS test database.
    """
    if backend == BACKEND_ONPREM:
        return onprem_database_std_params
    elif backend == BACKEND_SAAS:
        return saas_std_params
    raise ValueError(f"Unknown backend {backend}")


@pytest.fixture(scope="session")
def bucketfs_std_params(
    backend, onprem_bucketfs_std_params, saas_std_params
) -> dict[str, Any]:
    """
    This is a collection of StdParams parameters required to connect
    to the BucketFS on either DockerDB or SaaS test database.
    """
    if backend == BACKEND_ONPREM:
        return onprem_bucketfs_std_params
    elif backend == BACKEND_SAAS:
        return saas_std_params
    raise ValueError(f"Unknown backend {backend}")


def _cli_params_to_args(cli_params) -> str:
    def arg_string(k: str, v: Any):
        # This should have been implemented as a method of StdParams.
        k = k.replace("_", "-")
        if isinstance(v, bool):
            return f"--{k}" if v else f"--no-{k}"
        return f'--{k} "{v}"'

    return " ".join(arg_string(k, v) for k, v in cli_params.items())


@pytest.fixture(scope="session")
def database_cli_args(database_std_params) -> str:
    """
    CLI argument string for testing a command that involves connecting to the database.
    """
    return _cli_params_to_args(database_std_params)


@pytest.fixture(scope="session")
def bucketfs_cli_args(bucketfs_std_params) -> str:
    """
    CLI argument string for testing a command that involves connecting to the BucketFS .
    """
    return _cli_params_to_args(bucketfs_std_params)


@pytest.fixture(scope="session")
def cli_args(database_std_params, bucketfs_std_params):
    """
    CLI argument string for testing a command that involves connecting to both
    the database and the BucketFS.
    """
    std_params = dict(database_std_params)
    std_params.update(bucketfs_std_params)
    return _cli_params_to_args(std_params)
