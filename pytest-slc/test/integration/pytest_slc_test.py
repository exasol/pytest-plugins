from pathlib import Path
import requests
import textwrap

import pyexasol
from exasol.python_extension_common.deployment.language_container_validator import temp_schema


SLC_NAME = "template-Exasol-all-python-3.10_release.tar.gz"
SLC_VERSION = "8.0.0"
SLC_URL = ("https://github.com/exasol/script-languages-release/releases/"
           f"download/{SLC_VERSION}/{SLC_NAME}")


def download_container(save_dir: Path) -> Path:
    response = requests.get(SLC_URL, allow_redirects=True)
    response.raise_for_status()
    container_path = save_dir / SLC_NAME
    container_path.write_bytes(response.content)
    return container_path


def assert_udf_running(conn: pyexasol.ExaConnection, language_alias: str):
    with temp_schema(conn) as schema:
        udf_name = 'TEST_UDF'
        conn.execute(textwrap.dedent(f"""
            CREATE OR REPLACE {language_alias} SCALAR SCRIPT {schema}."{udf_name}"()
            RETURNS BOOLEAN AS
            def run(ctx):
                return True
            /
            """))
        result = conn.execute(f'SELECT {schema}."{udf_name}"()').fetchall()
        assert result[0][0] is True


def test_upload_slc(upload_slc, backend_aware_database_params, tmp_path):

    container_path = download_container(tmp_path)
    language_alias = 'PYTHON3_PYTEST_SLC'

    upload_slc(container_file_path=container_path, language_alias=language_alias)
    assert_udf_running(pyexasol.connect(**backend_aware_database_params), language_alias)
