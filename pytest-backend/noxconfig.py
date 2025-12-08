"""Configuration for nox based task runner"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    MutableMapping,
)
from pathlib import Path
from typing import (
    Any,
)

from exasol.toolbox.config import BaseConfig
from nox import Session


class Config(BaseConfig):
    """Project specific configuration used by nox infrastructure"""

    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    version_file: Path = (
        Path(__file__).parent / "exasol" / "pytest_backend" / "version.py"
    )
    path_filters: Iterable[str] = ("dist", ".eggs", "venv", "metrics-schema")
    source: Path = Path("exasol/pytest_backend")

    @staticmethod
    def pre_integration_tests_hook(
        _session: Session, _config: Config, _context: MutableMapping[str, Any]
    ) -> bool:
        """Implement if project specific behaviour is required"""
        return True

    @staticmethod
    def post_integration_tests_hook(
        _session: Session, _config: Config, _context: MutableMapping[str, Any]
    ) -> bool:
        """Implement if project specific behaviour is required"""
        return True


PROJECT_CONFIG = Config(
    # Restrict Python versions as difficulty with some unit tests for Python 3.14
    # This will be resolved in:
    #    https://github.com/exasol/pytest-plugins/issues/133
    python_versions=("3.10", "3.11", "3.12", "3.13"),
    # Uses SaaS; not ITDE DB versions
    exasol_versions=(),
)
