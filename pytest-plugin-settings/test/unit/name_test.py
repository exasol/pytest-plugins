import pytest
from exasol.pytest_plugin_settings import Name


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "name"),
        ("pytest-name", "pytest_name"),
        ("--arg-name", "arg_name"),
        ("--foo-arg-name", "foo_arg_name"),
        ("pytest-name-", "pytest_name"),
        ("pytest-name-2", "pytest_name_2"),
    ],
)
def test_normalize(name, expected):
    actual = Name.normalize(name)
    assert actual == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "NAME"),
        ("pytest-name", "PYTEST_NAME"),
        ("--arg-name", "ARG_NAME"),
        ("--foo-arg-name", "FOO_ARG_NAME"),
        ("pytest-name-", "PYTEST_NAME"),
        ("pytest-name-2", "PYTEST_NAME_2"),
    ],
)
def test_to_env(name, expected):
    actual = Name.to_env(name)
    assert actual == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "--name"),
        ("pytest-name", "--pytest-name"),
        ("--arg-name", "--arg-name"),
        ("--foo-arg-name", "--foo-arg-name"),
        ("pytest-name-", "--pytest-name"),
        ("pytest-name-2", "--pytest-name-2"),
    ],
)
def test_to_cli(name, expected):
    actual = Name.to_cli(name)
    assert actual == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "name"),
        ("pytest-name", "pytest_name"),
        ("--arg-name", "arg_name"),
        ("--foo-arg-name", "foo_arg_name"),
        ("pytest-name-", "pytest_name"),
        ("pytest-name-2", "pytest_name_2"),
    ],
)
def test_to_pytest(name, expected):
    actual = Name.to_pytest(name)
    assert actual == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("name", "name"),
        ("pytest-name", "pytest_name"),
        ("--arg-name", "arg_name"),
        ("--foo-arg-name", "foo_arg_name"),
        ("pytest-name-", "pytest_name"),
        ("pytest-name-2", "pytest_name_2"),
        ("PYTEST-NAME-2", "pytest_name_2"),
    ],
)
def test_name_instance_to_str(name, expected):
    actual = str(Name(name))
    assert actual == expected
