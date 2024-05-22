# pytest-exasol-saas Plugin

The `pytest-exasol-saas` plugin is a pytest plugin designed to facilitate the integration
testing of projects using the [exasol-saas-api](https://github.com/exasol/saas-api-python).

## Features

* **Integration with exasol-saas-api**: Designed to work closely with the exasol-saas-api.
* **Ease of Use:** Simplifies the configuration and execution of tests by leveraging the pytest framework, making it accessible to developers familiar with pytest conventions.

## Installation

To install the pytest-exasol-saas plugin, you can use pip:

```shell
pip install pytest-exasol-saas
```

## Database Instances

### Using an Existing Database Instance

By default the fixtures in pytest-exasol-saas Plugin will create instances of Exasol SaaS database with scope `session`.

If you want to use an existing instance instead, then you can provide the instance's ID with the command line option `--saas-database-id <ID>` to pytest.

### Keeping Database Instances After the Test Session

By default the fixtures in pytest-exasol-saas Plugin will remove the created database instances after the session or in case of errors.

However, if you provide the command line option `--keep-saas-database` then the pytest-exasol-saas plugin will _keep_ these instances for subsequent inspection or reuse.

Please note hat long-running instances will cause significant costs.

### Naming Database Instances

pytest-exasol-saas Plugin will name the database instances using 3 components

* **Project Short Tag**: Abbreviation of the current project, see below for different [options for providing the project short tag](#options-for-providing-the-project-short-tag).
* **Timestamp**: Number of seconds since epoc, see [Unix Time](https://en.wikipedia.org/wiki/Unix_time).
* A dash character `-`
* **User Name**: Login name of the current user.

A database instances might for example have the name `1715155224SAPIPY-run` indicating it was
* created on Wednesday, May 8, 2024
* in the context of a project with short tag `SAPIPY`
* by a user with login name starting with `run`

Please note that Exasol SaaS limits the length of database names to 10 characters only. So pytest-exasol-saas plugin will shorten the constructed name to 10 characters max.

If running your tests on a server for Continuous Integration (CI) then the name of the user might be not very expressive.

### Options for providing the Project Short Tag

* In yaml file `error_code_config.yml` in the project's root directory
* CLI option `--project-short-tag <short tag>` to pytest
* Environment variable `PROJECT_SHORT_TAG`
