PROJECTS := "pytest-slc pytest-extension pytest-backend pytest-saas pytest-itde"

# Default target
default:
    just --list

# Run tests for one or multiple projects within this respository
test +projects=PROJECTS:
    #!/usr/bin/env python3
    import subprocess, sys
    rc = 0
    def run(command):
        global rc
        result = subprocess.run(command.split())
        rc = result.returncode or rc

    for p in "{{projects}}".split():
        run(f"poetry -C {p}/ install")
        run(f"poetry -C {p}/ run nox -f {p}/noxfile.py -s coverage")
    sys.exit(rc)

relock +projects=PROJECTS:
    #!/usr/bin/env python3
    import subprocess, sys
    rc = 0
    def run(command):
        global rc
        result = subprocess.run(command.split())
        rc = result.returncode or rc

    for p in "{{projects}}".split():
        run(f"poetry -C {p}/ update")
    sys.exit(rc)

# Create a release
release project:
    @echo "Ensure environment variables are set:"
    @echo "- POETRY_HTTP_BASIC_PYPI_USERNAME=__token__"
    @echo "- POETRY_HTTP_BASIC_PYPI_PASSWORD=<your token>"
    #!/usr/bin/env bash
    poetry -C $(pwd)/{{project}}/ build
    poetry -C $(pwd)/{{project}}/ publish
