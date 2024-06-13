from collections.abc import MappingView
from collections import ChainMap
from dataclasses import dataclass
from typing import (
    Generic,
    Optional,
    TypeVar,
    Iterable,
)
from enum import Enum, auto


class Name:
    @staticmethod
    def normalize(name: str) -> str:
        name = name.replace("-", "_")
        name = name.lower()
        name = name.strip('_')
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
    def pytest(self) -> str:
        return self.normalized_name.pytest()

    @property
    def help(self) -> str:
        if not self.default:
            return f"{self.help_text}."
        return f"{self.help_text} (default: {self.default})."


class Group:
    def __init__(self, name: str, settings: Iterable[Setting]):
        group_name = Name.normalize(name)
        self._name = group_name
        self._settings = tuple(
            Setting(
                prefix=group_name,
                name=f"{setting.prefix}-{setting.name}",
                type=setting.type,
                help_text=setting.help_text,
            )
            for setting in settings
        )

    @property
    def settings(self):
        return self._settings


class Category(Enum):
    Environment = auto()
    CommandLine = auto()


class Resolver(MappingView):
    def __init__(
        self, settings: Iterable[Setting], environment=None, cli_arguments=None
    ):
        self._settings = tuple(settings)
        self._default = {s.normalized_name: s.default for s in self._settings}
        self._env = environment or {}
        self._cli = cli_arguments or {}
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

    def _environment(self, environment):
        env = {
            setting.normalized_name: setting.type(environment[setting.env])
            for setting in self._settings
            if setting.env in environment
        }
        self._env.update(env)

    def _cli(self, cli_arguments):
        cli = {
            setting.normalized_name: getattr(cli_arguments, setting.pytest)
            for setting in self.options
            if hasattr(cli_arguments, setting.pytest)
            and getattr(cli_arguments, setting.pytest) is not None
        }
        self._cli.update(cli)

    def update(self, mapping, category):
        dispatcher = {
            Category.Environment: self._environment,
            Category.CommandLine: self._cli,
        }
        method = dispatcher[category]
        method(mapping)
