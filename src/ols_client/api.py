# -*- coding: utf-8 -*-

import json
import logging
import os
import time

import requests

__all__ = [
    'OLS_BASE',
    'iterate_response_terms',
    'iterate_ontology_terms',
    'get_labels',
]

log = logging.getLogger(__name__)


def get_config():
    """Gets the configuration for this project from the default JSON file, or writes one if it doesn't exist

    :rtype: dict
    """
    p = os.path.join(os.path.expanduser('~'), '.config', 'ols_client')

    if not os.path.exists(p):
        os.makedirs(p)

    cp = os.path.join(p, 'config.json')

    if os.path.exists(cp):
        with open(cp) as f:
            return json.load(f)

    cfg = {'BASE': 'http://www.ebi.ac.uk/ols/api'}

    with open(cp, 'w') as f:
        json.dump(cfg, f, indent=2, sort_keys=True)

    return cfg


config = get_config()

OLS_BASE = config['BASE']


class OlsClient:
    def __init__(self, ols_base=None):
        self.base = ols_base if ols_base is not None else OLS_BASE


def iterate_response_terms(response):
    embedded = response['_embedded']

    terms = embedded['terms']

    for term in terms:
        yield term


def iterate_ontology_terms(ontology_name, ols_base=None, size=500):
    """Iterates over all terms, lazily with paging

    EBI says 500 is max size
    """
    ols_base = ols_base or OLS_BASE
    url = '{}/ontologies/{}/terms'.format(ols_base.rstrip('/'), ontology_name)

    t = time.time()
    response = requests.get(url, params={'size': size}).json()
    links = response['_links']

    for x in iterate_response_terms(response):
        yield x

    t = time.time() - t

    log.info(
        'Page %s/%s done in %.2f seconds',
        response['page']['number'],
        response['page']['totalPages'],
        t
    )

    log.info('Estimated time until done: %.2f', t * response['page']['totalPages'] / 60)

    while 'next' in links:
        t = time.time()
        response = requests.get(links['next']['href'], params={'size': size}).json()
        links = response['_links']

        for x in iterate_response_terms(response):
            yield x

        log.info(
            'Page %s/%s done in %.2f seconds',
            response['page']['number'],
            response['page']['totalPages'],
            time.time() - t
        )


def get_labels(ontology_name, ols_base=None):
    """Iterates over the labels of terms in the ontology

    :param str ontology_name:
    :param str ols_base:
    """
    log.info('Getting data from %s', ontology_name)
    for term in iterate_ontology_terms(ontology_name, ols_base):
        yield term['label']


def get_metadata(ontology_name, ols_base=None):
    ols_base = ols_base or OLS_BASE
    url = '{}/ontologies/{}'.format(ols_base.rstrip('/'), ontology_name)
    response = requests.get(url).json()
    return response


def get_description(ontology_name, ols_base=None):
    """Gets the description of a given ontology"""
    return get_metadata(ontology_name)['config'].get('description')
