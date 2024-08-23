"""
@pytest.fixture(scope='session', autouse=True)
def extension_build_slc_async(export_slc_async):
    with language_container_factory() as slc_builder:
        yield export_slc_async(slc_builder)

@pytest.fixture(scope='session')
def extension_upload_slc(extension_build_slc_async, upload_slc):
    upload_slc(*extension_build_slc_async, 'optional_bucketfs_path')
"""
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
    def func(slc_builder: LanguageContainerBuilder, *args, **kwargs):
        if use_onprem or use_saas:
            @paralleltask
            def export_runner():
                # export_result = slc_builder.export(*args, **kwargs)
                # yield export_result
                yield None

            with export_runner() as export_task:
                yield slc_builder, export_task
        else:
            yield slc_builder, None
    return func


@pytest.fixture(scope="session")
def upload_slc(backend_aware_database_params,
               backend_aware_bucketfs_params):
    def func(slc_builder: LanguageContainerBuilder,
             export_task,
             bucketfs_path: str = '') -> bool:
        if export_task is None:
            return False
        export_result = export_task.get_output()
        if export_result is None:
            return False

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
        return True

    return func
