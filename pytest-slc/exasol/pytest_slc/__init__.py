from __future__ import annotations

import getpass
from pathlib import Path

import exasol.bucketfs as bfs
import pytest
from exasol.pytest_backend import paralleltask
from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder,
)
from exasol.python_extension_common.deployment.language_container_deployer import (
    LanguageActivationLevel,
    LanguageContainerDeployer,
)
from exasol.slc.models.export_container_result import (
    ExportContainerResult,  # type: ignore
)
from exasol_integration_test_docker_environment.lib.api.api_errors import (
    TaskFailures,
    TaskRuntimeError,
)

SKIP_SLC_OPTION = "--skip-slc"
BFS_CONTAINER_DIRECTORY = "container"


def pytest_addoption(parser):
    parser.addoption(
        SKIP_SLC_OPTION, action="store_true", default=False, help="Skip SLC deployment"
    )


@pytest.fixture(scope="session")
def slc_builder() -> LanguageContainerBuilder | None:
    """
    This fixture must be provided by the user. Below is a simple implementation.

    @pytest.fixture(scope='session')
    def slc_builder():
        with language_container_factory() as container_builder:
            yield container_builder

    Here the language_container_factory is a context-manager function that creates a
    LanguageContainerBuilder object. This function performs all necessary preparations for
    building a language container, but does not call its export function. The idea is to share
    the code that builds a language container for the release and for integration tests.
    """
    return None


@pytest.fixture(scope="session", autouse=True)
def export_slc_async(
    request,
    slc_builder: LanguageContainerBuilder,
    use_onprem: bool,
    use_saas: bool,
):
    """
    The fixture starts the export() function of the provided
    LanguageContainerBuilder object as an asynchronous task.

    The operation will be skipped if none of the backends is in use or the
    container builder is not defined or the SLC deployment is skipped.
    """
    skip_slc = request.config.getoption(SKIP_SLC_OPTION)
    if skip_slc or (not (use_onprem or use_saas)) or (slc_builder is None):
        yield None
        return

    @paralleltask
    def export_runner():
        yield slc_builder.export()

    with export_runner() as export_task:
        # a "return" statement waits for export_runner().__exit__() while
        # "yield" does not not.
        #
        # In this case the SLC building takes quite long and this fixture
        # should not wait until the SLC building is completed.
        yield export_task


@pytest.fixture(scope="session")
def export_slc(slc_builder, export_slc_async) -> Path | None:
    """
    The fixture waits for the LanguageContainerBuilder.export() function to finish.
    It returns the path of the exported container.
    """
    if (slc_builder is None) or (export_slc_async is None):
        # Perhaps none of the backends is enabled, or we don't need the SLC deployment.
        return None

    try:
        export_result = export_slc_async.get_output()
        export_info = export_result.export_infos[str(slc_builder.flavor_path)][
            "release"
        ]
        return Path(export_info.cache_file)
    except TaskRuntimeError as ex:
        if isinstance(ex.__cause__, TaskFailures) or not ex.inner:
            raise
        else:
            # Handle the old way of error reporting
            failures = "\n".join(ex.inner)
            err_message = (
                f"SLC export ended with the following task failures:\n{failures}"
            )
            raise RuntimeError(err_message) from ex


@pytest.fixture(scope="session")
def language_alias(project_short_tag):
    """
    The user can override this fixture if they want to provide a more meaningful
    name for the language alias.
    """
    owner = getpass.getuser()
    return f"PYTHON3-{project_short_tag or 'EXTENSION'}-{owner}"


@pytest.fixture(scope="session")
def deploy_slc(
    slc_builder, export_slc, pyexasol_connection, backend_aware_bucketfs_params
):
    """
    The fixture provides a function deploying the language container in a database.
    The function can be called multiple times, allowing to activate the container with
    multiple aliases. However, the container will be uploaded only once.
    """
    bucket_file_path = ""

    def func(language_alias: str) -> None:
        nonlocal bucket_file_path
        if (slc_builder is not None) and (export_slc is not None):
            bucketfs_path = bfs.path.build_path(
                **backend_aware_bucketfs_params, path=BFS_CONTAINER_DIRECTORY
            )
            deployer = LanguageContainerDeployer(
                pyexasol_connection=pyexasol_connection,
                bucketfs_path=bucketfs_path,
                language_alias=language_alias,
            )
            if bucket_file_path:
                # The container has already been uploaded and just needs to be activated
                for alter_type in [
                    LanguageActivationLevel.Session,
                    LanguageActivationLevel.System,
                ]:
                    deployer.activate_container(
                        bucket_file_path, alter_type, allow_override=True
                    )
            else:
                bucket_file_path = export_slc.name
                deployer.run(
                    container_file=export_slc,
                    bucket_file_path=bucket_file_path,
                    alter_system=True,
                    allow_override=True,
                )

    return func


@pytest.fixture(scope="session")
def deployed_slc(deploy_slc, language_alias) -> None:
    """
    The fixture calls deploy_slc() once, with the language_alis defined in the fixture
    with the corresponded name.
    """
    deploy_slc(language_alias)
