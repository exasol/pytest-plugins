"""
A "Project Short Tag" is a short abbreviation for a project.

The pytest plugin for exasol-saas-api will include this short tag into the
names of created database instances to enable identifying the origin of
potentially long-running database instances in order to avoid unwanted costs.
"""

from __future__ import annotations

from pathlib import Path

import yaml

YML_FILE = "error_code_config.yml"
STOP_FILE = "pyproject.toml"


def _find_path_backwards(
    start_path: str | Path,
    stop_file: str | Path = STOP_FILE,
    target_path: str | Path = YML_FILE,
) -> Path | None:
    """
    An utility searching for a specified path backwards. It begins with the given start
    path and checks if the target path is among its siblings. Then it moves to the parent
    path and so on, until it either reaches the root of the file structure or finds the
    stop file. returns None if the search is unsuccessful.
    """
    current_path = Path(start_path)
    root = Path(current_path.root)
    while current_path != root:
        result_path = Path(current_path, target_path)
        if result_path.exists():
            return result_path
        stop_path = Path(current_path, stop_file)
        if stop_path.exists():
            return None
        current_path = current_path.parent
    return None


def read_from_yaml(start_dir: Path) -> str | None:
    """
    Read project-short-tag from yaml file ``FILE`` looking for it from the
    specified starting directory ``start_dir``.
    If the yml file cannot be found returns None.
    If the yml file is found, but it doesn't have the expected format raises
    a RuntimeError.
    """
    config_file = _find_path_backwards(start_dir)
    if config_file is None:
        return None
    with config_file.open("r") as file:
        ecc = yaml.safe_load(file)
        try:
            return next(t for t in ecc["error-tags"])
        except Exception as ex:
            raise RuntimeError(
                f"Could not read project short tag from file {config_file}"
            )
