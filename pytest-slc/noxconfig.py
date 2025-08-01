"""Configuration for nox based task runner"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    MutableMapping,
)
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
)

from nox import Session


@dataclass(frozen=True)
class Config:
    """Project specific configuration used by nox infrastructure"""

    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    version_file: Path = Path(__file__).parent / "exasol" / "pytest_slc" / "version.py"
    path_filters: Iterable[str] = ("dist", ".eggs", "venv", "metrics-schema", ".poetry")
    source: Path = Path("exasol/pytest_slc")
    python_versions = ["3.10", "3.11", "3.12", "3.13"]

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


PROJECT_CONFIG = Config()
