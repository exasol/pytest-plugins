PROJECTS := "pytest-saas pytest-itde"

# Default target
default:
    just --list

# Run tests for one or multiple projects within this respository
test +projects=PROJECTS:
    #!/usr/bin/env -S bash -eoE pipefail
    for p in {{projects}}; do
        poetry -C ${p}/ install
        poetry -C ${p}/ run nox -f ${p}/noxfile.py -s coverage
    done

# Create a release
release project version:
    @echo "ensure environment variables are set: POETRY_HTTP_BASIC_PYPI_USERNAME and POETRY_HTTP_BASIC_PYPI_PASSWORD"
    #!/usr/bin/env bash
    echo poetry -C {{project}}/ build
    echo poetry -C {{project}}/ publish
