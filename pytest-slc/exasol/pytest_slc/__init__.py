import os
import subprocess
from pathlib import Path
import time
from typing import Dict

import pytest
from _pytest.fixtures import FixtureRequest
from exasol_script_languages_container_tool.lib.tasks.export.export_info import ExportInfo
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer
import exasol.bucketfs as bfs

from exasol_transformers_extension.deployment import language_container
from tests.fixtures.database_connection_fixture import BACKEND_SAAS

LANGUAGE_ALIAS = "PYTHON3_TE"
CONTAINER_FILE_NAME = "exasol_transformers_extension_container.tar.gz"

SLC_EXPORT = pytest.StashKey[ExportInfo]()
SLC_UPLOADED = pytest.StashKey[Dict[str, bool]]()


@pytest.fixture(scope="session")
def flavor_path() -> Path:
    return language_container.find_flavor_path()


@pytest.fixture(scope="session")
def export_slc(request: FixtureRequest, flavor_path: Path) -> ExportInfo:
    if SLC_EXPORT not in request.session.stash:
        language_container.prepare_flavor(flavor_path=flavor_path)
        export_result = language_container.export(flavor_path=flavor_path)
        export_info = export_result.export_infos[str(flavor_path)]["release"]
        request.session.stash[SLC_EXPORT] = export_info
    return request.session.stash[SLC_EXPORT]


@pytest.fixture(scope="session")
def upload_slc(request: FixtureRequest, backend, bucketfs_location, pyexasol_connection,
               export_slc: ExportInfo) -> None:
    if SLC_UPLOADED not in request.session.stash:
        request.session.stash[SLC_UPLOADED] = dict()
    if backend not in request.session.stash[SLC_UPLOADED]:
        cleanup_images()

        container_file_path = Path(export_slc.cache_file)

        deployer = LanguageContainerDeployer(pyexasol_connection=pyexasol_connection,
                                             language_alias=LANGUAGE_ALIAS,
                                             bucketfs_path=bucketfs_location)

        deployer.run(container_file=container_file_path,
                     bucket_file_path=CONTAINER_FILE_NAME,
                     allow_override=True,
                     wait_for_completion=True)

        # Let's see if this helps
        if backend == BACKEND_SAAS:
            time.sleep(300)
        request.session.stash[SLC_UPLOADED][backend] = True


def cleanup_images():
    if "GITHUB_ACTIONS" in os.environ:
        # Remove image and build output to reduce the disk usage in CI.
        # We currently use Github Actions as the CI and its disk is limited to 14 GB.
        # TODO: This code can be removed when we move to a CI with larger disks.
        rm_docker_image = """docker images -a | grep 'transformers' | awk '{print $3}' | xargs docker rmi"""
        subprocess.run(rm_docker_image, shell=True)
