from __future__ import annotations

import os
import ssl
from datetime import timedelta
from typing import (
    Any,
    Generator,
)
from urllib.parse import urlparse

import pytest
from exasol.saas import client as saas_client
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    get_connection_params,
    timestamp_name,
)
from exasol_integration_test_docker_environment.lib import api
from exasol_integration_test_docker_environment.lib.data.environment_info import (
    EnvironmentInfo,
)

import exasol.pytest_backend.project_short_tag as pst

from .itde import (
    bucketfs_config,
    exasol_config,
    itde_config,
    itde_pytest_addoption,
    ssh_config,
)
from .parallel_task import paralleltask

BACKEND_OPTION = "--backend"
BACKEND_ONPREM = "onprem"
BACKEND_SAAS = "saas"
BACKEND_ALL = "all"


def pytest_addoption(parser):
    parser.addoption(
        BACKEND_OPTION,
        action="append",
        default=[],
        help=f"""List of test backends ({BACKEND_ONPREM}, {BACKEND_SAAS}). The target 
            backends must be specified explicitly. To select all backends add the argument 
            {BACKEND_OPTION}={BACKEND_ALL} to the command line. To select only one
            of the backends add the argument {BACKEND_OPTION}={BACKEND_ONPREM} or
            {BACKEND_OPTION}={BACKEND_SAAS} instead.
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
        """,
    )
    itde_pytest_addoption(parser)


def _is_backend_selected(request, backend: str) -> bool:
    backend_options = set(request.config.getoption(BACKEND_OPTION))
    return bool(backend_options.intersection({backend, BACKEND_ALL}))


@pytest.fixture(scope="session", params=[BACKEND_ONPREM, BACKEND_SAAS])
def backend(request) -> str:
    if not _is_backend_selected(request, request.param):
        pytest.skip()
    return request.param


@pytest.fixture(scope="session")
def use_onprem(request) -> bool:
    return _is_backend_selected(request, BACKEND_ONPREM)


@pytest.fixture(scope="session")
def use_saas(request) -> bool:
    return _is_backend_selected(request, BACKEND_SAAS)


@paralleltask
def start_itde(itde_config, exasol_config, bucketfs_config, ssh_config, database_name):
    """
    This function controls the ITDE with the help of parallelized
    version of the @contextmanager.
    """
    bucketfs_url = urlparse(bucketfs_config.url)
    env_info, cleanup_func = api.spawn_test_environment(
        environment_name=database_name,
        database_port_forward=exasol_config.port,
        bucketfs_port_forward=bucketfs_url.port,
        ssh_port_forward=ssh_config.port,
        db_mem_size=itde_config.db_mem_size,
        db_disk_size=itde_config.db_disk_size,
        nameserver=tuple(itde_config.nameserver),
        docker_db_image_version=itde_config.db_version,
    )
    yield env_info
    cleanup_func()


@pytest.fixture(scope="session", autouse=True)
def backend_aware_onprem_database_async(
    use_onprem, itde_config, exasol_config, bucketfs_config, ssh_config, database_name
):
    """
    If the onprem is a selected backend, this fixture starts brining up the ITDE and keeps
    it running for the duration of the session. It returns before the ITDE is ready. The
    "autouse" parameter assures that the ITDE, and other lengthy setup procedures are started
    preemptively before they are needed anywhere in the tests.

    The fixture shall not be used directly in tests.
    """
    if use_onprem and (itde_config.db_version != "external"):
        with start_itde(
            itde_config, exasol_config, bucketfs_config, ssh_config, database_name
        ) as itde_task:
            yield itde_task
    else:
        yield None


@pytest.fixture(scope="session")
def backend_aware_onprem_database(
    backend_aware_onprem_database_async,
) -> EnvironmentInfo | None:
    """
    If the onprem is a selected backend, this fixture waits till the ITDE becomes available.
    """
    if backend_aware_onprem_database_async is not None:
        return backend_aware_onprem_database_async.get_output()
    return None


def _env(var: str) -> str:
    result = os.environ.get(var)
    if result:
        return result
    raise RuntimeError(f"Environment variable {var} is empty.")


@pytest.fixture(scope="session")
def saas_host(use_saas) -> str:
    return _env("SAAS_HOST") if use_saas else ""


@pytest.fixture(scope="session")
def saas_pat(use_saas) -> str:
    return _env("SAAS_PAT") if use_saas else ""


@pytest.fixture(scope="session")
def saas_account_id(use_saas) -> str:
    return _env("SAAS_ACCOUNT_ID") if use_saas else ""


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
def saas_api_access(
    request, use_saas, saas_host, saas_pat, saas_account_id
) -> Generator[OpenApiAccess | None]:
    if use_saas and (not request.config.getoption("--saas-database-id")):
        client = create_saas_client(host=saas_host, pat=saas_pat)
        api_access = OpenApiAccess(client=client, account_id=saas_account_id)
        with api_access.allowed_ip():
            yield api_access
    else:
        yield None


@pytest.fixture(scope="session", autouse=True)
def backend_aware_saas_database_id_async(
    request, use_saas, database_name, saas_api_access
) -> Generator[str]:
    """
    If the saas is a selected backend, this fixture starts building a temporary SaaS
    database and keeps it running for the duration of the session. It returns before the
    database is ready. The "autouse" parameter assures that the SaaS database, and other
    lengthy setup procedures are started preemptively before they are needed anywhere in
    the tests.

    The fixture shall not be used directly in tests.
    """
    if saas_api_access is not None:
        keep = request.config.getoption("--keep-saas-database")
        idle_hours = float(request.config.getoption("--saas-max-idle-hours"))

        # Create a temporary database
        with saas_api_access.database(
            name=database_name, keep=keep, idle_time=timedelta(hours=idle_hours)
        ) as db:
            yield db.id
    elif use_saas:
        yield request.config.getoption("--saas-database-id")
    else:
        yield ""


@pytest.fixture(scope="session")
def backend_aware_saas_database_id(
    saas_api_access, backend_aware_saas_database_id_async
) -> Generator[str]:
    """
    If the saas is a selected backend, this fixture waits until the temporary SaaS database
    becomes available.
    """
    if saas_api_access is not None:
        saas_api_access.wait_until_running(backend_aware_saas_database_id_async)
    yield backend_aware_saas_database_id_async


@pytest.fixture(scope="session")
def backend_aware_onprem_database_params(
    use_onprem, backend_aware_onprem_database, exasol_config
) -> dict[str, Any]:
    if use_onprem:
        return {
            "dsn": f"{exasol_config.host}:{exasol_config.port}",
            "user": exasol_config.username,
            "password": exasol_config.password,
            "websocket_sslopt": {"cert_reqs": ssl.CERT_NONE},
        }
    return {}


@pytest.fixture(scope="session")
def backend_aware_saas_database_params(
    use_saas, saas_host, saas_pat, saas_account_id, backend_aware_saas_database_id
) -> dict[str, Any]:
    if use_saas:
        conn_params = get_connection_params(
            host=saas_host,
            account_id=saas_account_id,
            database_id=backend_aware_saas_database_id,
            pat=saas_pat,
        )
        conn_params["websocket_sslopt"] = {"cert_reqs": ssl.CERT_NONE}
        return conn_params
    return {}


@pytest.fixture(scope="session")
def backend_aware_onprem_bucketfs_params(
    use_onprem, backend_aware_onprem_database, bucketfs_config
) -> dict[str, Any]:
    if use_onprem:
        return {
            "backend": BACKEND_ONPREM,
            "url": bucketfs_config.url,
            "username": bucketfs_config.username,
            "password": bucketfs_config.password,
            "service_name": "bfsdefault",
            "bucket_name": "default",
            "verify": False,
        }
    return {}


@pytest.fixture(scope="session")
def backend_aware_saas_bucketfs_params(
    use_saas, saas_host, saas_pat, saas_account_id, backend_aware_saas_database_id
) -> dict[str, Any]:
    if use_saas:
        return {
            "backend": BACKEND_SAAS,
            "url": saas_host,
            "account_id": saas_account_id,
            "database_id": backend_aware_saas_database_id,
            "pat": saas_pat,
        }
    return {}


@pytest.fixture(scope="session")
def backend_aware_database_params(
    backend, backend_aware_onprem_database_params, backend_aware_saas_database_params
) -> dict[str, Any]:
    """
    Returns a set of parameters sufficient to open a pyexasol connection to the
    current testing backend.
    Usage example:
    connection = pyexasol.connect(**backend_aware_database_params, compression=True)
    """
    if backend == BACKEND_ONPREM:
        return backend_aware_onprem_database_params
    elif backend == BACKEND_SAAS:
        return backend_aware_saas_database_params
    raise ValueError(f"Unknown backend {backend}")


@pytest.fixture(scope="session")
def backend_aware_bucketfs_params(
    backend, backend_aware_onprem_bucketfs_params, backend_aware_saas_bucketfs_params
) -> dict[str, Any]:
    """
    Returns a set of parameters sufficient to open a PathLike bucket-fs connection to the
    current testing backend.
    Usage example:
    bfs_path = exasol.bucketfs.path.build_path(**backend_aware_bucketfs_params, path=path_in_bucket)
    """
    if backend == BACKEND_ONPREM:
        return backend_aware_onprem_bucketfs_params
    elif backend == BACKEND_SAAS:
        return backend_aware_saas_bucketfs_params
    raise ValueError(f"Unknown backend {backend}")
