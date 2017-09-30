# -*- coding: utf-8 -*-

import logging

from .client import OlsClient

__all__ = [
    'get_labels',
    'get_metadata',
]

log = logging.getLogger(__name__)


def get_labels(ontology, ols_base=None):
    """Iterates over the labels of terms in the ontology

    :param str ontology: The name of the ontology
    :param str ols_base: An optional, custom OLS base url
    :rtype: iter[str]
    """
    client = OlsClient(ols_base=ols_base)
    return client.iter_labels(ontology)


def get_metadata(ontology, ols_base=None):
    """Gets the metadata for a given ontology

    :param str ontology: The name of the ontology
    :param str ols_base: An optional, custom OLS base url
    :return: The dictionary representing the JSON from the OLS
    :rtype: dict
    """
    client = OlsClient(ols_base=ols_base)
    return client.get_metadata(ontology)
