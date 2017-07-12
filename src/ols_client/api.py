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

    response = requests.get(url, params={'size': size}).json()

    links = response['_links']

    log.info('On page %s of %s', response['page']['number'], response['page']['totalPages'])
    t = time.time()

    for x in iterate_response_terms(response):
        yield x

    log.info('Done in %.2f seconds', time.time() - t)

    while 'next' in links:
        response = requests.get(links['next']['href'], params={'size': size}).json()

        log.info('On page %s of %s', response['page']['number'], response['page']['totalPages'])
        t = time.time()

        for x in iterate_response_terms(response):
            yield x

        log.info('Done in %.2f seconds', time.time() - t)

        links = response['_links']


def get_labels(ontology_name, ols_base=None):
    ols_base = ols_base or OLS_BASE

    for term in iterate_ontology_terms(ontology_name, ols_base):
        yield term['label']


if __name__ == '__main__':
    import os

    logging.basicConfig(level=20)
    log.setLevel(20)
    with open(os.path.join(os.path.expanduser('~'), 'Desktop', 'chebi_from_ols.names'), 'w') as f:
        for label in get_labels('chebi'):
            print(label, file=f)
