from collections import ChainMap
from dataclasses import dataclass
from typing import (
    Generic,
    Optional,
    TypeVar,
)

from exasol_integration_test_docker_environment.lib.test_environment.ports import Ports

T = TypeVar("T")


@dataclass(frozen=True)
class ItdeOption(Generic[T]):
    name: str
    prefix: str
    type: T
    default: Optional[T] = None
    help_text: str = ""

    @property
    def env(self):
        """Environment variable name"""

        def normalize(name):
            name = name.replace("-", "_")
            name = name.upper()
            return name

        return f"{normalize(self.prefix)}_{normalize(self.name)}"

    @property
    def cli(self):
        """Cli argument name"""

        def normalize(name):
            name = name.replace("_", "-")
            name = name.lower()
            return name

        return f"--{normalize(self.prefix)}-{normalize(self.name)}"

    @property
    def pytest(self):
        """Pytest option name"""

        def normalize(name):
            name = name.replace("-", "_")
            name = name.lower()
            return name

        return f"{normalize(self.prefix)}_{normalize(self.name)}"

    @property
    def help(self):
        """Help text including information about default value."""
        if not self.default:
            return f"{self.help_text}."
        return f"{self.help_text} (default: {self.default})."


class ItdeOptionGroup:
    """
    Wraps a set of pytest options.
    """

    def __init__(self, prefix, options):
        self._prefix = prefix
        self._options = tuple(ItdeOption(prefix=prefix, **kwargs) for kwargs in options)
        self._default = {o.name: o.default for o in self._options}
        self._env = {}
        self._cli = {}
        self._kwargs = ChainMap(self._cli, self._env, self._default)

    @property
    def prefix(self):
        """The option group prefix."""
        return self._prefix

    @property
    def options(self):
        """A tuple of all options which are part of this group."""
        return self._options

    def kwargs(self, environment, cli_arguments):
        """
        Given the default values, the passed environment and cli arguments it will
        take care of the prioritization for the option values in regard of their
        source(s) and return a kwargs dictionary with all options and their
        appropriate value.
        """
        env = {
            o.name: o.type(environment[o.env])
            for o in self._options
            if o.env in environment
        }
        cli = {
            o.name: getattr(cli_arguments, o.pytest)
            for o in self.options
            if hasattr(cli_arguments, o.pytest)
            and getattr(cli_arguments, o.pytest) is not None
        }
        self._env.update(env)
        self._cli.update(cli)
        return self._kwargs


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


ONPREM_DB_OPTIONS = ItdeOptionGroup(
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

ONPREM_BFS_OPTIONS = ItdeOptionGroup(
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

SSH_OPTIONS = ItdeOptionGroup(
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


ITDE_OPTIONS = ItdeOptionGroup(
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

_ITDE_OPTION_GROUPS = (ONPREM_DB_OPTIONS, ONPREM_BFS_OPTIONS, ITDE_OPTIONS, SSH_OPTIONS)


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
