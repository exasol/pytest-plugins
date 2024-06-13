import pytest
from exasol.pytest_plugin_settings import Setting


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


def test_setting_help_without_default(verbose):
    expected = "Increase verbosity."
    actual = verbose.help
    assert actual == expected


def test_setting_help_with_default(log_level):
    expected = "Set the default log level (default: debug)."
    actual = log_level.help
    assert actual == expected


@pytest.mark.parametrize(
    "setting,expected",
    [
        (
            Setting(
                name="level",
                prefix="log",
                type=str,
                default="debug",
                help_text="Set the default log level",
            ),
            "log_level",
        ),
        (
            Setting(
                name="level",
                prefix="",
                type=str,
                default="debug",
                help_text="Set the default log level",
            ),
            "level",
        )
    ],
)
def test_normalized_name(setting, expected):
    actual = setting.normalized_name
    assert actual == expected
