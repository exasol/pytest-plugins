"""Configuration for nox based task runner"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Iterable,
    MutableMapping,
)

from nox import Session
from exasol.pytest_backend import (BACKEND_OPTION, BACKEND_ONPREM, BACKEND_SAAS)


@dataclass(frozen=True)
class Config:
    """Project specific configuration used by nox infrastructure"""

    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    version_file: Path = Path(__file__).parent / "exasol" / "pytest_backend" / "version.py"
    path_filters: Iterable[str] = ("dist", ".eggs", "venv", "metrics-schema")

    @staticmethod
    def pre_integration_tests_hook(
        _session: Session, _config: Config, _context: MutableMapping[str, Any]
    ) -> bool:
        """Implement if project specific behaviour is required"""
        fwd_args = _context.get('fwd-args', [])
        fwd_args.extend([BACKEND_OPTION, BACKEND_ONPREM, BACKEND_OPTION, BACKEND_SAAS])
        _context['fwd-args'] = fwd_args
        return True

    @staticmethod
    def post_integration_tests_hook(
        _session: Session, _config: Config, _context: MutableMapping[str, Any]
    ) -> bool:
        """Implement if project specific behaviour is required"""
        return True


PROJECT_CONFIG = Config()
