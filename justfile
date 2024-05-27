PROJECTS := "pytest-saas pytest-itde"

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

# Create a release
release project version:
    @echo "ensure environment variables are set: POETRY_HTTP_BASIC_PYPI_USERNAME and POETRY_HTTP_BASIC_PYPI_PASSWORD"
    #!/usr/bin/env bash
    echo poetry -C {{project}}/ build
    echo poetry -C {{project}}/ publish
