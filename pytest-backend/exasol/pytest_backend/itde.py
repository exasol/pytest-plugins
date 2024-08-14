import os
from dataclasses import dataclass
import pytest

from exasol_integration_test_docker_environment.lib.test_environment.ports import Ports
import exasol.pytest_backend.config as config


@dataclass
class OnpremDBConfig:
    """Exasol database configuration"""

    host: str
    port: int
    username: str
    password: str


@dataclass
class OnpremBfsConfig:
    """Bucketfs configuration"""

    url: str
    username: str
    password: str


@dataclass
class SshConfig:
    """SSH configuration"""

    port: int


@dataclass
class ItdeConfig:
    """Itde configuration settings"""

    db_version: str


_ONPREM_DB_OPTIONS = config.OptionGroup(
    prefix="exasol",
    options=(
        {
            "name": "host",
            "type": str,
            "default": "localhost",
            "help_text": "Host to connect to",
        },
        {
            "name": "port",
            "type": int,
            "default": Ports.forward.database,
            "help_text": "Port on which the exasol db is listening",
        },
        {
            "name": "username",
            "type": str,
            "default": "SYS",
            "help_text": "Username used to authenticate against the exasol db",
        },
        {
            "name": "password",
            "type": str,
            "default": "exasol",
            "help_text": "Password used to authenticate against the exasol db",
        },
    ),
)

_ONPREM_BFS_OPTIONS = config.OptionGroup(
    prefix="bucketfs",
    options=(
        {
            "name": "url",
            "type": str,
            "default": f"http://127.0.0.1:{Ports.forward.bucketfs}",
            "help_text": "Base url used to connect to the bucketfs service",
        },
        {
            "name": "username",
            "type": str,
            "default": "w",
            "help_text": "Username used to authenticate against the bucketfs service",
        },
        {
            "name": "password",
            "type": str,
            "default": "write",
            "help_text": "Password used to authenticate against the bucketfs service",
        },
    ),
)

_SSH_OPTIONS = config.OptionGroup(
    prefix="ssh",
    options=(
        {
            "name": "port",
            "type": int,
            "default": Ports.forward.ssh,
            "help_text": "Port on which external processes can access the database via SSH protocol",
        },
    ),
)


_ITDE_OPTIONS = config.OptionGroup(
    prefix="itde",
    options=(
        {
            "name": "db_version",
            "type": str,
            "default": "8.18.1",
            "help_text": "DB version to start, if value is 'external' an existing instance will be used",
        },
    ),
)

_ITDE_OPTION_GROUPS = (_ONPREM_DB_OPTIONS, _ONPREM_BFS_OPTIONS, _ITDE_OPTIONS, _SSH_OPTIONS)


def _add_option_group(parser, group):
    parser_group = parser.getgroup(group.prefix)
    for option in group.options:
        parser_group.addoption(
            option.cli,
            type=option.type,
            help=option.help,
        )


def itde_pytest_addoption(parser):
    for group in _ITDE_OPTION_GROUPS:
        _add_option_group(parser, group)


@pytest.fixture(scope="session")
def exasol_config(request) -> OnpremDBConfig:
    """Returns the configuration settings of the exasol db for this session."""
    cli_arguments = request.config.option
    kwargs = _ONPREM_DB_OPTIONS.kwargs(os.environ, cli_arguments)
    return OnpremDBConfig(**kwargs)


@pytest.fixture(scope="session")
def bucketfs_config(request) -> OnpremBfsConfig:
    """Returns the configuration settings of the bucketfs for this session."""
    cli_arguments = request.config.option
    kwargs = _ONPREM_BFS_OPTIONS.kwargs(os.environ, cli_arguments)
    return OnpremBfsConfig(**kwargs)


@pytest.fixture(scope="session")
def ssh_config(request) -> SshConfig:
    """Returns the configuration settings for SSH access in this session."""
    cli_arguments = request.config.option
    kwargs = _SSH_OPTIONS.kwargs(os.environ, cli_arguments)
    return SshConfig(**kwargs)


@pytest.fixture(scope="session")
def itde_config(request) -> ItdeConfig:
    """Returns the configuration settings of the ITDE for this session."""
    cli_arguments = request.config.option
    kwargs = _ITDE_OPTIONS.kwargs(os.environ, cli_arguments)
    return ItdeConfig(**kwargs)
