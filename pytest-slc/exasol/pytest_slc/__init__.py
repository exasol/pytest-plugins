from __future__ import annotations
from pathlib import Path
from exasol.pytest_backend import paralleltask
import pytest

import pyexasol
import exasol.bucketfs as bfs
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer
from exasol.python_extension_common.deployment.language_container_builder import LanguageContainerBuilder

BFS_CONTAINER_DIRECTORY = 'container'


@pytest.fixture(scope='session')
def slc_builder() -> LanguageContainerBuilder:
    raise NotImplementedError("The slc_builder fixture must be supplied by the user.")


@pytest.fixture(scope='session', autouse=True)
def export_slc_async(slc_builder: LanguageContainerBuilder, use_onprem: bool, use_saas: bool):
    """
    The fixture provides a helper function that starts the export() function of the provided
    LanguageContainerBuilder object as an asynchronous task. It must be called from a user's
    fixture. Below is a usage example:

    @pytest.fixture(scope='session', autouse=True)
    def extension_export_slc_async(export_slc_async):
        with language_container_factory() as container_builder:
            yield export_slc_async(container_builder)

    Here, the extension_export_slc_async is a user provided fixture. The
    language_container_factory is also a user provided context-manager function that creates
    a LanguageContainerBuilder object. This function performs all necessary preparations for
    building a language container, but does not call its export function. The idea is to share
    the code that builds a language container for the release and for integration tests.

    It is important to run the fixture with the autouse=True parameter. This is to make sure
    the container is being built asynchronously, in parallel with other lengthy task, like
    starting a temporary database.

    The container will not be built if none of the backends is in use.
    """
    if (not (use_onprem or use_saas)) or (slc_builder is None):
        return None

    @paralleltask
    def export_runner():
        yield slc_builder.export()

    with export_runner() as export_task:
        return export_task


@pytest.fixture(scope='session')
def export_slc(slc_builder, export_slc_async) -> Path | None:
    """
    The fixture provides a helper function that waits for the LanguageContainerBuilder.export()
    function to finish. It will then return the container path and the language alias. The
    expected input is the output of the export_slc_async. This fixture shall be called from a
    user provided fixture similar to the following.

    @pytest.fixture(scope='session')
    def extension_export_slc(extension_export_slc_async, export_slc):
        return export_slc(*extension_export_slc_async)
    """
    if (slc_builder is None) or (export_slc_async is None):
        # Perhaps none of the backends is enabled.
        return None

    export_result = export_slc_async.get_output()
    export_info = export_result.export_infos[str(slc_builder.flavor_path)]["release"]
    return Path(export_info.cache_file)


@pytest.fixture(scope="session")
def upload_slc(slc_builder, export_slc,
               backend_aware_database_params, backend_aware_bucketfs_params):
    """
    The fixture provides a helper function that uploads language container
    to a database. The expected input is the output of the export_slc, plus the optional path
    in the bucket-fs where the container should be uploaded. Like the previous two fixtures,
    it must be called from a user provided fixture, similar to this:

    @pytest.fixture(scope='session')
    def extension_upload_slc(extension_export_slc, upload_slc):
        upload_slc(*extension_export_slc, 'optional_bucketfs_path')
    """
    if (slc_builder is not None) and (export_slc is not None):
        pyexasol_connection = pyexasol.connect(**backend_aware_database_params)
        bucketfs_path = bfs.path.build_path(**backend_aware_bucketfs_params,
                                            path=BFS_CONTAINER_DIRECTORY)
        deployer = LanguageContainerDeployer(pyexasol_connection=pyexasol_connection,
                                             bucketfs_path=bucketfs_path,
                                             language_alias=slc_builder.language_alias)
        deployer.run(container_file=export_slc, alter_system=True, allow_override=True)
