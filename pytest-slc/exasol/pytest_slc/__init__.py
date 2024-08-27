from __future__ import annotations
from pathlib import Path
from exasol.pytest_backend import paralleltask
import pytest

import pyexasol
import exasol.bucketfs as bfs
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer
from exasol.python_extension_common.deployment.language_container_builder import LanguageContainerBuilder


@pytest.fixture(scope='session')
def export_slc_async(use_onprem, use_saas):
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
    def func(slc_builder: LanguageContainerBuilder, *args, **kwargs):
        if use_onprem or use_saas:
            @paralleltask
            def export_runner():
                yield slc_builder.export(*args, **kwargs)

            with export_runner() as export_task:
                return slc_builder, export_task
        else:
            return slc_builder, None
    return func


@pytest.fixture(scope='session')
def export_slc():
    """
    The fixture provides a helper function that waits for the LanguageContainerBuilder.export()
    function to finish. It will then return the container path and the language alias. The
    expected input is the output of the export_slc_async. This fixture shall be called from a
    user provided fixture similar to the following.

    @pytest.fixture(scope='session')
    def extension_export_slc(extension_export_slc_async, export_slc):
        return export_slc(*extension_export_slc_async)
    """
    def func(slc_builder: LanguageContainerBuilder | None, export_task):
        if (slc_builder is None) or (export_task is None):
            # Perhaps none of the backends is enabled.
            return None, None
        export_result = export_task.get_output()
        export_info = export_result.export_infos[str(slc_builder.flavor_path)]["release"]
        return Path(export_info.cache_file), slc_builder.language_alias
    return func


@pytest.fixture(scope="session")
def upload_slc(backend_aware_database_params,
               backend_aware_bucketfs_params):
    """
    The fixture provides a helper function that uploads language container
    to a database. The expected input is the output of the export_slc, plus the optional path
    in the bucket-fs where the container should be uploaded. Like the previous two fixtures,
    it must be called from a user provided fixture, similar to this:

    @pytest.fixture(scope='session')
    def extension_upload_slc(extension_export_slc, upload_slc):
        upload_slc(*extension_export_slc, 'optional_bucketfs_path')
    """
    def func(container_path: Path | None, language_alias: str | None, bucketfs_path: str = ''):
        if container_path and language_alias:
            pyexasol_connection = pyexasol.connect(**backend_aware_database_params)
            bucketfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path=bucketfs_path)
            deployer = LanguageContainerDeployer(pyexasol_connection=pyexasol_connection,
                                                 bucketfs_path=bucketfs_path,
                                                 language_alias=language_alias)
            deployer.run(container_file=Path(container_path), alter_system=True, allow_override=True)
    return func
