from textwrap import dedent

import pytest

from exasol.pytest_backend.project_short_tag import (
    STOP_FILE,
    YML_FILE,
    read_from_yaml,
)


def test_read_from_yaml(tmp_path):
    start_dir = tmp_path / "start_dir"
    short_tag = "ABC"
    short_tag_file = tmp_path / YML_FILE
    with short_tag_file.open("w") as f:
        f.write(
            dedent(
                f"""
        error-tags:
            {short_tag}:
                highest-index: 0
        """
            )
        )
    assert read_from_yaml(start_dir) == short_tag


def test_read_from_yaml_not_found(tmp_path):
    start_dir = tmp_path / "start_dir"
    stop_file = tmp_path / STOP_FILE
    with stop_file.open("w") as f:
        f.write("[tool.poetry]")
    assert read_from_yaml(start_dir) is None


def test_read_from_yaml_invalid(tmp_path):
    start_dir = tmp_path / "start_dir"
    short_tag_file = tmp_path / YML_FILE
    with short_tag_file.open("w") as f:
        f.write(
            dedent(
                f"""
        whatever:
            ABC:
                highest-index: 0
        """
            )
        )
    with pytest.raises(RuntimeError):
        read_from_yaml(start_dir)
