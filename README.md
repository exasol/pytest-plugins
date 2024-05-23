# Pytest-Plugins for Exasol

Welcome to the official repository for Exasol pytest-plugins!

This collection of plugins is designed to enhance and simplify the testing experience for projects related to Exasol.

By providing a centralized location for pytest plugins, we aim to foster collaboration, ensure consistency, and improve the quality of testing practices within the organization.

## Introduction

[pytest](https://pytest.org) is a powerful testing framework for [python](https://www.python.org), and with the help of these plugins, developers can extend its functionality to better suit the testing requirements of Exasol-related projects.

Whether you're looking to use database interactions, enhance test reporting, or streamline your testing pipeline, our plugins are here to help.

## Plugins

| Plugin        | Description                                                                                                                | PYPI                                                               |
|---------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `pytest-itde` | Fixture to enable simple usage with Exasol's project [ITDE](https://github.com/exasol/integration-test-docker-environment) | [pytest-exasol-itde](https://pypi.org/project/pytest-exasol-itde/) |
| `pytest-saas` | Fixture to enable simple usage with Exasol's project [saas-api-python](https://github.com/exasol/saas-api-python/)         | [pytest-exasol-saas](https://pypi.org/project/pytest-exasol-saas/) |


## Installation

To ensure you're using the latest features and bug fixes, we recommend installing the plugins directly from PyPI using your preferred package manager. This approach simplifies the process of keeping your testing environment up-to-date.

For example, to install the `pytest-itde` plugin, you could use the following command:


```shell
pip install pytest-itde
```

To install a specific version of a plugin, simply specify the version number:

```shell
pip install "pytest-itde==x.y.z"
```

Replace x.y.z with the desired version number.

## Development

Before you can start developing in this workspace, please ensure you have the following tools installed either globally or at a workspace level.

* [Python](https://www.python.org)
* [Just](https://github.com/casey/just)

## Run Tests

### Slow Tests

Some of the test cases verify connecting to a SaaS database instance and
execution will take about 20 minutes.

These test cases are only executed by the following GitHub workflows
* `ci-main.yml`
* `ci-slow.yml`

Both of these workflows can be run manually, workflow `ci-main.yml` is executed automatically at the 7th day of each month.

For merging a pull request to branch `main` workflow `ci-slow.yml` needs to be run and terminate successfully.
