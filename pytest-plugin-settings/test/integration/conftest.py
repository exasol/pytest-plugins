import pytest
from inspect import cleandoc

pytest_plugins = "pytester"


@pytest.fixture()
def conftest(pytester):
    file = pytester.path.joinpath("conftest.py")
    file.write_text(
        cleandoc(
            """
            import pytest
            from exasol.pytest_plugin_settings import Group, Setting, PytestResolver,  add_to_pytest_settings
            
            PORT = Setting(prefix='', name="port", type=int, default=9999, help_text="Port to connect to")
            ADDRESS = Setting(prefix='', name="ip", type=str, default="127.0.0.1", help_text="IP to connect to")
            
            CREDENTIALS = Group(name='credentials', settings=[
                Setting(prefix=None, name="user", type=str, default="johndoe", help_text="Username"),
                Setting(prefix=None, name="pw", type=str, default="password", help_text="Password")
            ])
            
            SETTINGS = [
                Setting(prefix=None, name="db-name", type=str, default="test.db", help_text="Name of the database"),
                Setting(prefix=None, name="db-schema", type=str, default="test_schema", help_text="name of the schema"),
            ]
                
            def pytest_addoption(parser):
                # add a single settings to pytest
                add_to_pytest_settings(PORT, parser)
                add_to_pytest_settings(ADDRESS, parser)
                # add a group of settings to pytest
                add_to_pytest_settings(CREDENTIALS, parser)
                # add a list of settings to pytest
                add_to_pytest_settings(SETTINGS, parser)
                
            def pytest_configure(config):
                all_settings = [ADDRESS, PORT] + [ s for s in CREDENTIALS.settings ] + SETTINGS
                settings = PytestResolver(all_settings, config)
                config.stash["my-plugin-settings"] = settings
                
            @pytest.fixture()
            def my_settings(request):
                settings = request.config.stash["my-plugin-settings"]
                yield settings
                
            @pytest.fixture()
            def port(my_settings):
                yield my_settings["port"]
                
            @pytest.fixture()
            def ip(my_settings):
                yield my_settings["ip"]
                
            @pytest.fixture()
            def user(my_settings):
                yield my_settings["credentials_user"]
                
            @pytest.fixture()
            def password(my_settings):
                yield my_settings["credentials_pw"]
            """
        )
    )
    file = pytester.path.joinpath("test_smoke.py")
    file.write_text(
        cleandoc(
            """
            def test_settings(user, port):
                print()
                print(f"username: {user}")
                print(f"port: {port}")
                
            def test_smoke_fail():
                assert False
                
            def test_smoke_succeed():
                assert True
            """
        )
    )


def test_basic_pytester(pytester, conftest):
    result = pytester.runpytest("-s", "-vvv", ".")
    #config = pytester.parseconfig()
    #configure = pytester.parseconfigure()
    result2 = pytester.runpytest("--help")
    print(result)
