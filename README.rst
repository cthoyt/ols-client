OLS Client
==========
A Python wrapper for accessing the RESTful API of the Ontology Lookup Service

Getting labels from ontology
----------------------------
>>> from ols_client import get_labels
>>>> labels = get_labels('chebi')

Getting labels from ontology using an alternative OLS
-----------------------------------------------------
>>> from ols_client import get_labels
>>> labels = get_labels('chebi', ols_base='http://lookup.scaiview.com/ols-boot/api/')

Using the CLI
-------------
:code:`python3 -m ols_client labels chebi > chebi.txt`
