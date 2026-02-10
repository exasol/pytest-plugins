import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # noqa: F403, pylint: disable=wildcard-import disable=unused-wildcard-import

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]
