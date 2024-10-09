"""defines nox tasks/targets for this project"""
import sys

import nox
from nox import Session
from noxconfig import PROJECT_CONFIG

print(sys.path)
# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # pylint: disable=wildcard-import disable=unused-wildcard-import

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["fix"]


@nox.session(name="my-integration-tests", python=False)
def my_integration_tests(session: Session) -> None:
    path = PROJECT_CONFIG.root / "test" / "integration"
    base_command = ["poetry", "run"]
    pytest_command = ["pytest", "-v", "-s", f"{path}"]
    command = base_command + pytest_command
    session.run(*command)
