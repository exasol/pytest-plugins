from __future__ import annotations
from typing import Callable
from pathlib import Path
import pytest

import pyexasol
import exasol.bucketfs as bfs
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer


@pytest.fixture(scope="session")
def upload_slc(backend_aware_database_params,
               backend_aware_bucketfs_params) -> Callable[[str | Path, str, str], None]:

    def func(container_file_path: str | Path,
             language_alias: str,
             bucketfs_path: str = ''):
        pyexasol_connection = pyexasol.connect(**backend_aware_database_params)
        bucketfs_path = bfs.path.build_path(**backend_aware_bucketfs_params, path=bucketfs_path)
        deployer = LanguageContainerDeployer(pyexasol_connection=pyexasol_connection,
                                             bucketfs_path=bucketfs_path,
                                             language_alias=language_alias)
        deployer.run(container_file=Path(container_file_path), alter_system=True, allow_override=True)

    return func
