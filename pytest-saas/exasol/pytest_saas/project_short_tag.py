"""
A "Project Short Tag" is a short abbreviation for a project.

The pytest plugin for exasol-saas-api will include this short tag into the
names of created database instances to enable identifying the origin of
potentially long-running database instances in order to avoid unwanted costs.
"""

from pathlib import Path

FILE = "error_code_config.yml"


def read_from_yaml(dir: Path) -> str:
    """
    Read project-short-tag from yaml file ``FILE`` in the specified
    directory ``dir``.
    """
    config_file = dir / FILE
    if not config_file.exists():
        return None
    content = config_file.read_text()
    header = False
    for line in content.splitlines():
        line = line.strip()
        if header:
            print(line.strip().replace(":", ""))
            return
        if line.startswith("error-tags:"):
            header = True
    raise RuntimeError(f"Could not read project short tag from file {config_file}")
