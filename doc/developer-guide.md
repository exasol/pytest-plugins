# Developer Guide Exasol pytest-plugins

## Dependencies

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
