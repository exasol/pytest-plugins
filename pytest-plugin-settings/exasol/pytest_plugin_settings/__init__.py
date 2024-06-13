import os
import pytest
from functools import singledispatch
from collections.abc import IterableABC as IterableAbc
from collections.abc import MappingView
from collections import ChainMap
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar, Iterable
from enum import Enum, auto


class Name:
    @staticmethod
    def normalize(name: str) -> str:
        name = name.replace("-", "_")
        name = name.lower()
        name = name.strip("_")
        return name

    @staticmethod
    def to_env(name: str) -> str:
        name = Name.normalize(name)
        name = name.upper()
        return name

    @staticmethod
    def to_cli(name: str) -> str:
        name = Name.normalize(name)
        name = name.replace("_", "-")
        return f"--{name}"

    @staticmethod
    def to_ini(name: str) -> str:
        name = Name.normalize(name)
        name = name.replace("_", "-")
        return name

    @staticmethod
    def to_pytest(name: str) -> str:
        name = Name.normalize(name)
        return name

    def __init__(self, name: str):
        self._name = Name.normalize(name)

    def __str__(self) -> str:
        return self._name

    @property
    def env(self) -> str:
        return self.to_env(self._name)

    @property
    def cli(self) -> str:
        return self.to_cli(self._name)

    @property
    def ini(self) -> str:
        return self.to_ini(self._name)

    @property
    def pytest(self) -> str:
        return self.to_pytest(self._name)


T = TypeVar("T")


@dataclass(frozen=True)
class Setting(Generic[T]):
    name: str
    prefix: str
    type: T
    default: Optional[T] = None
    help_text: str = ""

    @property
    def normalized_name(self) -> str:
        return str(Name(f"{self.prefix}-{self.name}"))

    @property
    def env(self) -> str:
        return self.normalized_name.env()

    @property
    def cli(self) -> str:
        return self.normalized_name.cli()

    @property
    def ini(self) -> str:
        return self.normalized_name.ini()

    @property
    def pytest(self) -> str:
        return self.normalized_name.pytest()

    @property
    def help(self) -> str:
        if not self.default:
            return f"{self.help_text}."
        return f"{self.help_text} (default: {self.default})."


class Group:
    def __init__(self, name: str, settings: IterableAbc[Setting]):
        group_name = Name.normalize(name)
        self._name = group_name
        self._settings = tuple(
            Setting(
                prefix=group_name,
                name=f"{setting.prefix}-{setting.name}"
                if setting.prefix
                else setting.name,
                type=setting.type,
                help_text=setting.help_text,
            )
            for setting in settings
        )

    @property
    def name(self):
        return self._name

    @property
    def settings(self):
        return self._settings


class Category(Enum):
    ConfigFile = auto()
    Environment = auto()
    CommandLine = auto()


class Resolver(MappingView):
    def __init__(
        self,
        settings: IterableAbc[Setting],
        cli_arguments=None,
        environment=None,
        config=None,
    ):
        self._settings = tuple(settings)
        self._default = {s.normalized_name: s.default for s in self._settings}
        self._config = {}
        self._env = {}
        self._cli = {}

        self.update(config, Category.ConfigFile)
        self.update(environment, Category.Environment)
        self.update(cli_arguments, Category.CommandLine)

        self._kwargs = ChainMap(self._cli, self._env, self._default)

    def __len__(self):
        return len(self._kwargs)

    def __getitem__(self, key):
        return self._kwargs[key]

    def __iter__(self):
        return iter(self._kwargs)

    @property
    def settings(self):
        return self._kwargs

    def update(self, mapping, category):
        dispatcher = {
            Category.CommandLine: self._update_cli,
            Category.Environment: self._update_environment,
            Category.ConfigFile: self._update_config_file,
        }
        method = dispatcher[category]
        method(mapping)

    def _update_cli(self, cli_arguments):
        cli = {
            setting.normalized_name: getattr(cli_arguments, setting.pytest)
            for setting in self.options
            if hasattr(cli_arguments, setting.pytest)
            and getattr(cli_arguments, setting.pytest) is not None
        }
        self._cli.update(cli)

    def _update_environment(self, environment):
        env = {
            setting.normalized_name: setting.type(environment[setting.env])
            for setting in self._settings
            if setting.env in environment
        }
        self._env.update(env)

    def _update_config_file(self, config):
        cfg = {
            setting.normalized_name: setting.type(config[setting.ini])
            for setting in self._settings
            if setting.ini in config
        }
        self._config.update(cfg)


class PytestResolver(Resolver):
    def __init__(self, settings: Iterable[Setting], config: pytest.Config):
        cli = from_pytest(settings, config)
        cfg = from_pytest_ini(settings, config)
        env = os.environ
        super().__init__(cli_arguments=cli, environment=env, config=cfg)


def from_pytest(settings: Iterable[Setting], config: pytest.Config) -> Dict[str, Any]:
    pass


def from_env(settings: Iterable[Setting], env: Dict[str, str]) -> Dict[str, Any]:
    pass


def from_pytest_ini(
    settings: Iterable[Setting], config: pytest.Config
) -> Dict[str, Any]:
    pass


@singledispatch
def add_to_pytest_settings(obj, parser):
    raise TypeError("Unsupported type")


@add_to_pytest_settings.register
def _(setting: Setting, parser):
    parser.addoption(setting.cli, help=setting.help)
    parser.addini(name=setting.ini, help=setting.help)


@add_to_pytest_settings.register
def _(settings: IterableAbc, parser):
    for setting in settings:
        add_to_pytest_settings(setting, parser)


@add_to_pytest_settings.register
def _(group: Group, parser):
    group_parser = parser.getgroup(group.name)
    add_to_pytest_settings(group.settings, group_parser)


# Write to readme and test, plugin should use the following hooks

# def pytest_configure(config: pytest.Config):
#   # Add settings/group to parser using add_to_pytest
#   add_to_pytest(my_group)

# def pytest_configure(config: pytest.Config):
#   # hook up settings resolver and store in stash?
#   pass
