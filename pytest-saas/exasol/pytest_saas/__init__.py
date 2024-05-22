import os
from pathlib import Path

import pytest
from exasol.saas.client import openapi
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    timestamp_name,
)

import exasol.pytest_saas.project_short_tag as pst


def pytest_addoption(parser):
    parser.addoption(
        f"--saas-database-id",
        help="""ID of the instance of an existing SaaS database to be
            used during the current pytest session instead of creating a
            dedicated instance temporarily.""",
    )
    parser.addoption(
        f"--keep-saas-database",
        action="store_true",
        default=False,
        help="""Keep the SaaS database instance created for the current
            pytest session for subsequent inspection or reuse.""",
    )
    parser.addoption(
        f"--project-short-tag",
        help="""Short tag aka. "abbreviation" for your current project.
            See docstring in project_short_tag.py for more details.
            pytest plugin for exasol-saas-api will include this short tag into
            the names of created database instances.""",
    )


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
def saas_database(
    request, api_access, database_name
) -> openapi.models.database.Database:
    """
    Note: The SaaS instance database returned by this fixture initially
    will not be operational. The startup takes about 20 minutes.
    """
    db_id = request.config.getoption("--saas-database-id")
    if db_id:
        yield api_access.get_database(db_id)
        return
    with api_access.database(database_name) as db:
        yield db


@pytest.fixture(scope="session")
def operational_saas_database_id(api_access, saas_database) -> str:
    db = saas_database
    api_access.add_allowed_ip()
    api_access.wait_until_running(db.id)
    return db.id
