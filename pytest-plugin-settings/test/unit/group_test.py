import pytest
from exasol.pytest_plugin_settings import Setting, Group


@pytest.fixture
def verbose():
    yield Setting(
        name="verbose",
        prefix="",
        type=bool,
        default=None,
        help_text="Increase verbosity",
    )


@pytest.fixture
def log_level():
    yield Setting(
        name="level",
        prefix="logging",
        type=str,
        default="debug",
        help_text="Set the default log level",
    )


def test_group_name():
    group = Group(name="mygroup", settings=[])
    expected = "mygroup"
    actual = group.name
    assert actual == expected


def test_group_setting_without_prefix(verbose):
    group = Group(name="mygroup", settings=[verbose])
    expected = "mygroup_verbose"
    group_setting = group.settings[0]
    actual = group_setting.normalized_name
    assert actual == expected


def test_group_setting_wit_prefix(log_level):
    group = Group(name="mygroup", settings=[log_level])
    expected = "mygroup_logging_level"
    group_setting = group.settings[0]
    actual = group_setting.normalized_name
    assert actual == expected
