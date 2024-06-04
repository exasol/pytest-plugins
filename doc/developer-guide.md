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

## Release

`pytest-plugins` is a multi-project repository. Each of the plugins can be released independently.

Releasing a single plugin includes
* Publishing to pypi
* Creating a release on GitHub

This requires a dedicated Git-tag for each release of each plugin.  The convention is to use the name of the plugin as a prefix followed by a dash character and the version of the plugin, e.g. `pytest-saas-0.1.0`.

In order to create a release for one of the plugins
1. Open the GitHub repository in your browser
2. On top select the tab "Actions"
3. On the left hand side select action "Continous Delivery (Release)"
4. On the right hand click button "Run workflow"
5. Select banch "main"
6. Select the project, e.g. "pytest-saas"
7. Enter the version number, e.g. `0.2.0`
8. Click the button "Run workflow"

The workflow will then
* Checkout the project
* Build the selected plugin
* Publish it to pypi
* Create a Git-tag and a GitHub release using the naming convention described above
