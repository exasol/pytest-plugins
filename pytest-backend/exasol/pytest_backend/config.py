from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass
from typing import (
    Generic,
    Optional,
    TypeVar,
)

T = TypeVar("T")


@dataclass(frozen=True)
class Option(Generic[T]):
    name: str
    prefix: str
    type: T
    default: T | None = None
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


class OptionGroup:
    """
    Wraps a set of pytest options.
    """

    def __init__(self, prefix, options):
        self._prefix = prefix
        self._options = tuple(Option(prefix=prefix, **kwargs) for kwargs in options)
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
