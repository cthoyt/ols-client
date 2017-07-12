# -*- coding: utf-8 -*-

import logging
import time

import requests

__all__ = [
    'OLS_BASE',
    'iterate_response_terms',
    'iterate_ontology_terms',
    'get_labels',
]

log = logging.getLogger(__name__)

OLS_BASE = 'http://www.ebi.ac.uk/ols/api/ontologies/{}/terms'


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
    url = ols_base.format(ontology_name)

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
    """Iterates over the labels of terms in the ontology"""
    log.info('Getting data from %s', ontology_name)
    for term in iterate_ontology_terms(ontology_name, ols_base):
        yield term['label']


if __name__ == '__main__':
    import os

    logging.basicConfig(level=20)
    log.setLevel(20)

    with open(os.path.join(os.path.expanduser('~'), 'Desktop', 'chebi_from_ols.names'), 'w') as f:
        for label in get_labels('chebi'):
            print(label, file=f)
