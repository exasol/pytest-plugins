.. _pytest-plugins-exasol:

Pytest-Plugins for Exasol
==========================

Welcome to the official repository for Exasol pytest-plugins!
This collection of plugins is designed to enhance and simplify the testing experience for projects related to Exasol.
By providing a centralized location for pytest plugins, we aim to foster collaboration, ensure consistency, and improve the quality of testing practices within the organization.

Introduction
------------

`pytest <https://pytest.org>`_ is a powerful testing framework for `python <https://www.python.org>`_, and with the help of these plugins, developers can extend its functionality to better suit the testing requirements of Exasol-related projects.
Whether you're looking to use database interactions, enhance test reporting, or streamline your testing pipeline, our plugins are here to help.

Plugins
-------

.. list-table::
   :header-rows: 1

   * - Plugin
     - Description
     - PYPI
   * - pytest-itde
     - fixture to enable simple usage with exasols itde proejct
     - TBD

Installation
------------

To ensure you're using the latest features and bug fixes, we recommend installing the plugins directly from PyPI using your preferred package manager. This approach simplifies the process of keeping your testing environment up-to-date.

For example, to install the ``pytest-itde`` plugin, you could use the following command:

.. code-block:: bash

    pip install pytest-itde

To install a specific version of a plugin, simply specify the version number:

.. code-block:: bash

    pip install "pytest-itde==x.y.z"

Replace x.y.z with the desired version number.

Development
-----------

Before you can start developing in this workspace, please ensure you have the following tools installed either globally or at a workspace level.

- `Python <https://www.python.org>`_
- `Just <https://github.com/casey/just>`_

Run Tests
---------

Slow Tests
^^^^^^^^^^

Some of the test cases verify connecting to a SaaS database instance and execution will take about 20 minutes.

These test cases are disabled by default and will only be executed when the commit message contains the string `[run-slow-tests]`.
