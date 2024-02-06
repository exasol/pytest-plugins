PROJECTS := "pytest-itde"

# Default target
default:
    just --list

# Reformat all python files in the respository
fmt:
   ruff format
   ruff --fix 

# Run tests for one or multiple projects within this respository
test +projects=PROJECTS:
    #!/usr/bin/env bash
    for p in {{projects}}; do
        poetry -C ${p}/ install
        poetry -C ${p}/ run pytest ${p}/test
    done
