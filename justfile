PROJECTS := "pytest-itde"

# Default target
default:
    just --list

# Run tests for one or multiple projects within this respository
test +projects=PROJECTS:
    #!/usr/bin/env bash
    for p in {{projects}}; do
        poetry -C ${p}/ install
        poetry -C ${p}/ run nox -f ${p}/noxfile.py -s coverage
    done
