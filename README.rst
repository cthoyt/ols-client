OLS Client |build| |coverage| |documentation|
=============================================
A Python wrapper for accessing the RESTful API of the Ontology Lookup Service.


Since the creation of this repository, the EBI has also generated their own client that
can be found at https://github.com/Ensembl/ols-client and on PyPI as
`ebi-ols-client <https://pypi.org/project/ebi-ols-client/>`_.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
Install the latest stable version from PyPI

.. code:: sh

    $ python3 -m pip install ols_client

Install the latest version directly from GitHub

.. code:: sh

    $ python3 -m pip install git+https://github.com/cthoyt/ols-client.git

Cookbook
--------
Getting labels from ontology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> from ols_client import get_labels
>>> labels = get_labels('chebi')

Getting labels from ontology using an alternative OLS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> from ols_client import get_labels
>>> labels = get_labels('chebi', ols_base='http://lookup.scaiview.com/ols-boot/api/')

Using the CLI
~~~~~~~~~~~~~
.. code:: sh

    $ python3 -m ols_client labels chebi > chebi.txt

.. |build| image:: https://travis-ci.org/cthoyt/ols-client.svg?branch=master
    :target: https://travis-ci.org/cthoyt/ols-client
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/cthoyt/ols-client/coverage.svg?branch=master
    :target: https://codecov.io/gh/cthoyt/ols-client?branch=master
    :alt: Coverage Status

.. |documentation| image:: https://readthedocs.org/projects/ols-client/badge/?version=stable
    :target: http://ols-client.readthedocs.io/en/stable/
    :alt: Documentation Status

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/ols-client.svg
    :alt: Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/ols-client.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/ols-client.svg
    :alt: MIT License
