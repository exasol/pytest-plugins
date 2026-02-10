# Unreleased

## Summary

This release fixes vulnerabilites by updating dependencies.

Additionally project `pytest-extension` was removed, as it has been moved to a separate GitHub repository https://github.com/exasol/pytest-extension.

## Security

* #164: Fixed vulnerabilities by updating dependencies

## Refactorings

* #140: Ensured that a proper project-short-tag is used in SaaS tests.
* #141: Added a Merge Gate to the CI Workflow.
* #146: Relocked transitive dependency filelock
* #150: Updated user guide and added instructions for (re-)using an external or local database to the `README`
* #162: Removed plugin pytest-extension
