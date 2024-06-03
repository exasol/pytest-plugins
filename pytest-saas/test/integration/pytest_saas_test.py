import os
import re
from inspect import cleandoc
from unittest import mock

import pytest

pytest_plugins = "pytester"


@pytest.fixture
def make_test_files():
    def make(pytester, files):
        pytester.makepyfile(**files)

    return make


def _testfile(body):
    testname = re.sub(r"^.*def ([^(]+).*", "\\1", body, flags=re.S)
    return { testname: cleandoc(body) }


def _cli_args(*args):
    return args


def _env(**kwargs):
    return kwargs


@pytest.mark.parametrize(
    "files,cli_args",
    [
        ( _testfile("""
          def test_no_cli_args(request):
              assert not request.config.getoption("--keep-saas-database")
              assert request.config.getoption("--saas-database-id") is None
          """),
          _cli_args(),
         ),
        ( _testfile("""
          import os
          def test_cli_args(request):
              assert request.config.getoption("--keep-saas-database")
              assert "123" == request.config.getoption("--saas-database-id")
              assert "PST" == request.config.getoption("--project-short-tag")
          """),
          _cli_args(
              "--keep-saas-database",
              "--project-short-tag", "PST",
              "--saas-database-id", "123",
          ),
         ),
    ])
def test_pass_options_via_cli(pytester, make_test_files, files, cli_args):
    """
    This test could also be called a unit test and verifies that the CLI
    arguments are registered correctly, can be passed to pytest, and are
    accessible within external test cases.
    """
    make_test_files(pytester, files)
    result = pytester.runpytest(*cli_args)
    assert result.ret == pytest.ExitCode.OK


@pytest.mark.parametrize(
    "pst_file, pst_env, pst_cli, expected",
    [
        ("F", None, None, "F"),
        ("F", "E",  None, "E"),
        ("F", "E",  "C",  "C"),
    ])
def test_project_short_tag(
        request,
        pytester,
        pst_file,
        pst_env,
        pst_cli,
        expected,
):
    """
    This test sets different values for project short tag in file
    error_code_config.yml, cli option --project-short-tag, and environment
    variable PROJECT_SHORT_TAG and verifies the precedence.
    """
    if pst_file:
        pytester.makefile(".yml", **{
            "error_code_config":
            cleandoc(f"""
            error-tags:
              {pst_file}:
                highest-index: 0
            """)
        })
    pytester.makepyfile(** _testfile(
        f"""
        def test_project_short_tag(project_short_tag):
            assert "{expected}" == project_short_tag
        """))
    env = { "PROJECT_SHORT_TAG": pst_env } if pst_env else {}
    cli_args = [ "--project-short-tag", pst_cli ] if pst_cli else []
    with mock.patch.dict(os.environ, env):
        result = pytester.runpytest(*cli_args)
    assert result.ret == pytest.ExitCode.OK


def test_id_of_existing_database(request, pytester, capsys):
    """
    Use an invalid ID and verify that exasol-saas-api signals an error
    because that there is no database with the specified ID.
    """
    testname = request.node.name
    pytester.makepyfile(** _testfile(f"""
          def {testname}(saas_database):
              pass
          """))
    result = pytester.runpytest("--saas-database-id", "123")
    captured = capsys.readouterr()
    assert result.ret != pytest.ExitCode.OK
    assert "Database not found" in captured.out


@pytest.mark.slow
def test_operational_database(request, pytester):
    testname = request.node.name
    pytester.makepyfile(** _testfile(f"""
    def {testname}(operational_saas_database_id):
        assert operational_saas_database_id is not None
    """))
    result = pytester.runpytest()
    assert result.ret == pytest.ExitCode.OK


def test_keep_database(request, pytester, api_access, capsys):
    testname = request.node.name
    pytester.makepyfile(** _testfile(f"""
    def {testname}(saas_database):
        db = saas_database
        print(f"\\ndatabase-id: {{db.id}}")
    """))
    id = None
    try:
        result = pytester.runpytest("--keep-saas-database", "-s")
        assert result.ret == pytest.ExitCode.OK
        captured = capsys.readouterr()
        for line in captured.out.splitlines():
            if line.startswith("database-id: "):
                id = line.split()[1]
    finally:
        if id:
            api_access.delete_database(id)
