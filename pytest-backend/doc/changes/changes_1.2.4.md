# 1.2.4 - 2025-12-10

## Summary 

This release removes the override `8.18.0` in favor of using the default Docker DB version as defined by ITDE.

## Features

* #139: Removed override `8.18.0` for default Docker DB version used by ITDE

## Bug fixing

* #135: Made fixtures leading to pyexasol_connection yielding the result rather than returning it.

## Dependency Updates

### `main`
* Updated dependency `exasol-integration-test-docker-environment` to `5.0.0`
