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


# Create a release
release project version:
    @echo "This currently is a stub, in the future the workflow probably will look somthing like this:"
    @echo ""
    @echo "poetry -C {{project}} run -f {{project}}/noxfile -s release {{ version }}"
    @echo ""
    @echo ""
    @echo "Workflow:"
    @echo "* update version"
    @echo "* rename unreleased section to specified version"
    @echo "* rename create new empty unreleased section"
    @echo "* create git tag"
    @echo "* build package/wheel"
    @echo "* create & publish github release"
    @echo "* create & publish pypi release"
    @echo "* create/output slack announcement and print to terminal"

