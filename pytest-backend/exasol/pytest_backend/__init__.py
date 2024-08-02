from __future__ import annotations
from typing import Any
from datetime import timedelta
from contextlib import ExitStack
import ssl
import pytest

from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    get_connection_params
)

from exasol.pytest_itde import bootstrap_db

_BACKEND_ONPREM = 'onprem'
_BACKEND_SAAS = 'saas'


def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        action="append",
        default=[],
        help="""List of test backends (onprem, saas). By default, the tests will be
            run on both backends. To select only one of the backends add the
            argument --backend=<name-of-the-backend> to the command line. Both backends
            can be selected like ... --backend=onprem --backend=saas, but this is the
            same as the default.
            """,
    )


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        backend_options = metafunc.config.getoption("--backend")
        if not backend_options:
            backend_options = [_BACKEND_ONPREM, _BACKEND_SAAS]
        metafunc.parametrize("backend", backend_options)


@pytest.fixture
def backend(request) -> str:
    return request.param


def _is_backend_selected(request, backend: str) -> bool:
    backend_options = request.config.getoption("--backend")
    if backend_options:
        return backend in backend_options
    else:
        return True


@pytest.fixture(scope='session')
def use_onprem(request) -> bool:
    return _is_backend_selected(request, _BACKEND_ONPREM)


@pytest.fixture(scope='session')
def use_saas(request) -> bool:
    return _is_backend_selected(request, _BACKEND_SAAS)


@pytest.fixture(scope="session")
def backend_aware_onprem_database(use_onprem,
                                  itde_config,
                                  exasol_config,
                                  bucketfs_config,
                                  ssh_config) -> None:
    if use_onprem:
        with bootstrap_db(itde_config=itde_config,
                          exasol_config=exasol_config,
                          bucketfs_config=bucketfs_config,
                          ssh_config=ssh_config):
            yield
    else:
        yield


@pytest.fixture(scope="session")
def backend_aware_saas_database_id(request,
                                   use_saas,
                                   database_name,
                                   saas_host,
                                   saas_pat,
                                   saas_account_id) -> str:
    if use_saas:
        db_id = request.config.getoption("--saas-database-id")
        keep = request.config.getoption("--keep-saas-database")
        idle_hours = float(request.config.getoption("--saas-max-idle-hours"))

        with ExitStack() as stack:
            # Create and configure the SaaS client.
            client = create_saas_client(host=saas_host, pat=saas_pat)
            api_access = OpenApiAccess(client=client, account_id=saas_account_id)
            stack.enter_context(api_access.allowed_ip())

            if db_id:
                # Return the id of an existing database if it's provided
                yield db_id
            else:
                # Create a temporary database and waite till it becomes operational
                db = stack.enter_context(api_access.database(
                    name=database_name,
                    keep=keep,
                    idle_time=timedelta(hours=idle_hours)))
                api_access.wait_until_running(db.id)
                yield db.id
    else:
        yield ''


@pytest.fixture(scope="session")
def backend_aware_onprem_database_params(use_onprem,
                                         backend_aware_onprem_database,
                                         exasol_config) -> dict[str, Any]:
    if use_onprem:
        return {
            'dsn': f'{exasol_config.host}:{exasol_config.port}',
            'user': exasol_config.username,
            'password': exasol_config.password,
            'websocket_sslopt': {'cert_reqs': ssl.CERT_NONE}
        }
    return {}


@pytest.fixture(scope="session")
def backend_aware_saas_database_params(use_saas,
                                       saas_host,
                                       saas_pat,
                                       saas_account_id,
                                       backend_aware_saas_database_id) -> dict[str, Any]:
    if use_saas:
        conn_params = get_connection_params(host=saas_host,
                                            account_id=saas_account_id,
                                            database_id=backend_aware_saas_database_id,
                                            pat=saas_pat)
        conn_params['websocket_sslopt'] = {'cert_reqs': ssl.CERT_NONE}
        return conn_params
    return {}


@pytest.fixture(scope="session")
def backend_aware_onprem_bucketfs_params(use_onprem,
                                         backend_aware_onprem_database,
                                         bucketfs_config) -> dict[str, Any]:
    if use_onprem:
        return {
            'backend': _BACKEND_ONPREM,
            'url': bucketfs_config.url,
            'username': bucketfs_config.username,
            'password': bucketfs_config.password,
            'service_name': 'bfsdefault',
            'bucket_name': 'default',
            'verify': False
        }
    return {}


@pytest.fixture(scope="session")
def backend_aware_saas_bucketfs_params(use_saas,
                                       saas_host,
                                       saas_pat,
                                       saas_account_id,
                                       backend_aware_saas_database_id) -> dict[str, Any]:
    if use_saas:
        return {
            'backend': _BACKEND_SAAS,
            'url': saas_host,
            'account_id': saas_account_id,
            'database_id': backend_aware_saas_database_id,
            'pat': saas_pat
        }
    return {}


@pytest.fixture
def backend_aware_database_params(backend,
                                  backend_aware_onprem_database_params,
                                  backend_aware_saas_database_params) -> dict[str, Any]:
    """
    Returns a set of parameters sufficient to open a pyexasol connection to the
    current testing backend.
    Usage example:
    connection = pyexasol.connect(**backend_aware_database_params, compression=True)
    """
    if backend == _BACKEND_ONPREM:
        return backend_aware_onprem_database_params
    elif backend == _BACKEND_SAAS:
        return backend_aware_saas_database_params
    else:
        ValueError(f'Unknown backend {backend}')


@pytest.fixture
def backend_aware_bucketfs_params(backend,
                                  backend_aware_onprem_bucketfs_params,
                                  backend_aware_saas_bucketfs_params) -> dict[str, Any]:
    """
    Returns a set of parameters sufficient to open a PathLike bucket-fs connection to the
    current testing backend.
    Usage example:
    bfs_path = exasol.bucketfs.path.build_path(**backend_aware_bucketfs_params, path=path_in_bucket)
    """
    if backend == _BACKEND_ONPREM:
        return backend_aware_onprem_bucketfs_params
    elif backend == _BACKEND_SAAS:
        return backend_aware_saas_bucketfs_params
    else:
        ValueError(f'Unknown backend {backend}')
