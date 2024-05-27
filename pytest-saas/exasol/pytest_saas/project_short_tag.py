"""
A "Project Short Tag" is a short abbreviation for a project.

The pytest plugin for exasol-saas-api will include this short tag into the
names of created database instances to enable identifying the origin of
potentially long-running database instances in order to avoid unwanted costs.
"""

from pathlib import Path
import yaml

FILE = "error_code_config.yml"


def read_from_yaml(dir: Path) -> str:
    """
    Read project-short-tag from yaml file ``FILE`` in the specified
    directory ``dir``.
    """
    config_file = dir / FILE
    if not config_file.exists():
        return None
    with open(config_file, 'r') as file:
        ecc = yaml.safe_load(file)
        try:
            return next(t for t in ecc["error-tags"])
        except Exception as ex:
            raise RuntimeError(f"Could not read project short tag from file {config_file}")
