# 1.2.5 - 2026-02-10

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

## Dependency Updates

### `main`
* Updated dependency `exasol-saas-api:2.5.0` to `2.6.0`

### `dev`
* Updated dependency `exasol-toolbox:3.0.0` to `5.1.1`
