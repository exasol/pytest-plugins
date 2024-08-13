import os
import pytest
from exasol_integration_test_docker_environment.lib.test_environment.ports import Ports

from exasol.pytest_backend import itde_config

EXASOL = itde_config.OptionGroup(
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

BUCKETFS = itde_config.OptionGroup(
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

SSH = itde_config.OptionGroup(
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


ITDE = itde_config.OptionGroup(
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

OPTION_GROUPS = (EXASOL, BUCKETFS, ITDE, SSH)


def _add_option_group(parser, group):
    parser_group = parser.getgroup(group.prefix)
    for option in group.options:
        parser_group.addoption(
            option.cli,
            type=option.type,
            help=option.help,
        )


def itde_pytest_addoption(parser):
    for group in OPTION_GROUPS:
        _add_option_group(parser, group)


@pytest.fixture(scope="session")
def exasol_config(request) -> itde_config.Exasol:
    """Returns the configuration settings of the exasol db for this session."""
    cli_arguments = request.config.option
    kwargs = EXASOL.kwargs(os.environ, cli_arguments)
    return itde_config.Exasol(**kwargs)


@pytest.fixture(scope="session")
def bucketfs_config(request) -> itde_config.BucketFs:
    """Returns the configuration settings of the bucketfs for this session."""
    cli_arguments = request.config.option
    kwargs = BUCKETFS.kwargs(os.environ, cli_arguments)
    return itde_config.BucketFs(**kwargs)


@pytest.fixture(scope="session")
def ssh_config(request) -> itde_config.Ssh:
    """Returns the configuration settings for SSH access in this session."""
    cli_arguments = request.config.option
    kwargs = SSH.kwargs(os.environ, cli_arguments)
    return itde_config.Ssh(**kwargs)


@pytest.fixture(scope="session")
def itde_config(request) -> itde_config.Itde:
    """Returns the configuration settings of the ITDE for this session."""
    cli_arguments = request.config.option
    kwargs = ITDE.kwargs(os.environ, cli_arguments)
    return itde_config.Itde(**kwargs)
