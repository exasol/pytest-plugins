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
    The fixture provides a helper function that calls the LanguageContainerBuilder.export()
    as a parallel task. Below is an expected usage:

    @pytest.fixture(scope='session', autouse=True)
    def extension_build_slc_async(export_slc_async):
        with language_container_factory() as container_builder:
            yield export_slc_async(container_builder)

    Here, the extension_build_slc_async is a user provided fixture. The
    language_container_factory is also a user provided context-manager function that creates
    a LanguageContainerBuilder object. This function performs all necessary preparations for
    building a language container, but does not call its export function. The idea is to share
    the functionality that builds the container for the release and for the integration tests.

    It is important to run the fixture with the autouse=True parameter. This way the container
    is being built asynchronously, in parallel with other lengthy task, like starting a
    temporary database.

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


@pytest.fixture(scope="session")
def upload_slc(backend_aware_database_params,
               backend_aware_bucketfs_params):
    """
    The fixture provides a helper function that uploads the language container
    built in the export_slc_async fixture. Here is an expected usage:

    @pytest.fixture(scope='session')
    def extension_upload_slc(extension_build_slc_async, upload_slc):
        upload_slc(*extension_build_slc_async, 'optional_bucketfs_path')

    The user provided extension_upload_slc fixture depends on another user provided
    fixture -  extension_build_slc_async. See the export_slc_async docstring for
    details.
    """
    def func(slc_builder: LanguageContainerBuilder,
             export_task,
             bucketfs_path: str = ''):
        if (slc_builder is None) or (export_task is None):
            # Perhaps none of the backends is enabled.
            return
        export_result = export_task.get_output()

        # Get the container parameters
        export_info = export_result.export_infos[str(slc_builder.flavor_path)]["release"]
        container_file_path = Path(export_info.cache_file)
        language_alias = slc_builder.language_alias

        # Upload the container to the database
        pyexasol_connection = pyexasol.connect(**backend_aware_database_params)
        bucketfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path=bucketfs_path)
        deployer = LanguageContainerDeployer(pyexasol_connection=pyexasol_connection,
                                             bucketfs_path=bucketfs_path,
                                             language_alias=language_alias)
        deployer.run(container_file=Path(container_file_path), alter_system=True, allow_override=True)

    return func
