from __future__ import annotations
from typing import Any
import os
from datetime import timedelta
from contextlib import ExitStack
import ssl
from urllib.parse import urlparse
import pytest

from exasol_integration_test_docker_environment.lib import api
from exasol.saas import client as saas_client
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    get_connection_params,
    timestamp_name
)
import exasol.pytest_backend.project_short_tag as pst
from exasol.pytest_backend.itde import (
    itde_pytest_addoption,
    exasol_config,
    bucketfs_config,
    ssh_config,
    itde_config
)

_BACKEND_OPTION = '--backend'
_BACKEND_ONPREM = 'onprem'
_BACKEND_SAAS = 'saas'

_onprem_stash_key = pytest.StashKey[bool]()
_saas_stash_key = pytest.StashKey[bool]()


def pytest_addoption(parser):
    parser.addoption(
        _BACKEND_OPTION,
        action="append",
        default=[],
        help=f"""List of test backends (onprem, saas). By default, the tests will be
            run on both backends. To select only one of the backends add the
            argument {_BACKEND_OPTION}=<name-of-the-backend> to the command line. Both
            backends can be selected like ... {_BACKEND_OPTION}=onprem {_BACKEND_OPTION}=saas,
            but this is the same as the default.
            """,
    )
    parser.addoption(
        "--project-short-tag",
        help="""Short tag aka. "abbreviation" for your current project.
            See docstring in project_short_tag.py for more details.
            pytest plugin for exasol-saas-api will include this short tag into
            the names of created database instances.""",
    )
    parser.addoption(
        "--saas-database-id",
        help="""ID of the instance of an existing SaaS database to be
            used during the current pytest session instead of creating a
            dedicated instance temporarily.""",
    )
    parser.addoption(
        "--keep-saas-database",
        action="store_true",
        default=False,
        help="""Keep the SaaS database instance created for the current
            pytest session for subsequent inspection or reuse.""",
    )
    parser.addoption(
        "--saas-max-idle-hours",
        action="store",
        default=saas_client.Limits.AUTOSTOP_DEFAULT_IDLE_TIME.total_seconds() / 3600,
        help="""
        The SaaS cluster would normally stop after a certain period of inactivity. 
        The default period is 2 hours. For some tests, this period is too short.
        Use this parameter to set a sufficient idle period in the number of hours.
        """
    )
    itde_pytest_addoption(parser)


@pytest.fixture(scope='session', params=[_BACKEND_ONPREM, _BACKEND_SAAS])
def backend(request) -> str:
    backend_options = request.config.getoption(_BACKEND_OPTION)
    if backend_options and (request.param not in backend_options):
        pytest.skip()
    return request.param


def _is_backend_selected(request, backend: str) -> bool:
    backend_options = request.config.getoption(_BACKEND_OPTION)
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
def backend_aware_onprem_database(request,
                                  use_onprem,
                                  itde_config,
                                  exasol_config,
                                  bucketfs_config,
                                  ssh_config,
                                  database_name) -> None:
    if use_onprem and (itde_config.db_version != "external"):
        # Guard against a potential issue with repeated call of a parameterised fixture
        if _onprem_stash_key in request.session.stash:
            raise RuntimeError(('Repeated call of the session level fixture '
                                'backend_aware_onprem_database'))
        request.session.stash[_onprem_stash_key] = True

        bucketfs_url = urlparse(bucketfs_config.url)
        _, cleanup_function = api.spawn_test_environment(
            environment_name=database_name,
            database_port_forward=exasol_config.port,
            bucketfs_port_forward=bucketfs_url.port,
            ssh_port_forward=ssh_config.port,
            db_mem_size="4GB",
            docker_db_image_version=itde_config.db_version,
        )
        yield
        cleanup_function()
    else:
        yield


def _env(var: str) -> str:
    result = os.environ.get(var)
    if result:
        return result
    raise RuntimeError(f"Environment variable {var} is empty.")


@pytest.fixture(scope="session")
def saas_host() -> str:
    return _env("SAAS_HOST")


@pytest.fixture(scope="session")
def saas_pat() -> str:
    return _env("SAAS_PAT")


@pytest.fixture(scope="session")
def saas_account_id() -> str:
    return _env("SAAS_ACCOUNT_ID")


@pytest.fixture(scope="session")
def project_short_tag(request):
    return (
        request.config.getoption("--project-short-tag")
        or os.environ.get("PROJECT_SHORT_TAG")
        or pst.read_from_yaml(request.config.rootpath)
    )


@pytest.fixture(scope="session")
def database_name(project_short_tag):
    return timestamp_name(project_short_tag)


@pytest.fixture(scope="session")
def api_access(saas_host, saas_pat, saas_account_id) -> OpenApiAccess:
    with create_saas_client(saas_host, saas_pat) as client:
        yield OpenApiAccess(client, saas_account_id)


@pytest.fixture(scope="session")
def backend_aware_saas_database_id(request,
                                   use_saas,
                                   database_name,
                                   saas_host,
                                   saas_pat,
                                   saas_account_id) -> str:
    if use_saas:
        # Guard against a potential issue with repeated call of a parameterised fixture
        if _saas_stash_key in request.session.stash:
            raise RuntimeError(('Repeated call of the session level fixture '
                                'backend_aware_saas_database_id'))
        request.session.stash[_saas_stash_key] = True

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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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
