# Pytest-Plugins for Exasol

Welcome to the official repository for Exasol pytest-plugins!

This collection of plugins is designed to enhance and simplify the testing experience for projects related to Exasol.

By providing a centralized location for pytest plugins, we aim to foster collaboration, ensure consistency, and improve the quality of testing practices within the organization.

Please note that pytest plugin pytest-exasol-extension has been moved to a separate repository https://github.com/exasol/pytest-extension.

## Introduction

[pytest](https://pytest.org) is a powerful testing framework for [python](https://www.python.org), and with the help of these plugins, developers can extend its functionality to better suit the testing requirements of Exasol-related projects.

Whether you're looking to use database interactions, enhance test reporting, or streamline your testing pipeline, our plugins are here to help.

## Plugins

| Plugin                    | Description                                                                                                                | PYPI                                                                         |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|
| `pytest-exasol-backend`   | Fixture aggregating functionality of both of the above plugins                                                             | [pytest-exasol-backend](https://pypi.org/project/pytest-exasol-backend/)     |

## Installation

To ensure you're using the latest features and bug fixes, we recommend installing the plugins directly from PyPI using your preferred package manager. This approach simplifies the process of keeping your testing environment up-to-date.

For example, to install the `pytest-exasol-backend` plugin, you could use the following command:


```shell
pip install pytest-exasol-backend
```

To install a specific version of a plugin, simply specify the version number:

```shell
pip install "pytest-exasol-backend==x.y.z"
```

Replace x.y.z with the desired version number.

## Development

See [Developer Guide](doc/developer-guide.md).

## Archived plugins

* `pytest-itde`
* `pytest-saas`
