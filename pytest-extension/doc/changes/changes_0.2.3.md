# 0.2.3 - 2025-06-13

Code name: Dependency upgrade on top of 0.2.2.

## Summary

This release upates dependencies on top of version 0.2.2.

In particular this release establishes compatibility with potentially breaking changes in transitive dependency `saas-api-python` version `1.0.0` via `pytest-exasol-backend` version `0.4.0`

## Refactorings

* #90 Relocked dependencies, updated exasol-toolbox to ^1.0.0, updated to poetry 2.1.2
* Relocked dependencies, updated exasol-toolbox to ^1.3.0
* #99: Updated dependencies

## Dependency Updates

Compared to version pytest-extension-0.2.2 this release updates the following dependencies:

### File `pyproject.toml`

* Updated dependency `pytest-exasol-backend:0.3.2` to `0.4.0`
* Updated dependency `exasol-python-extension-common:0.8.0` to `0.10.0`
* Updated dependency `exasol-toolbox:0.20.0` to `1.4.0`
* Updated dependency `exasol-bucketfs:1.0.1` to `1.1.0`
* Updated dependency `click:8.1.8` to `8.2.1`
