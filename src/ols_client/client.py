# -*- coding: utf-8 -*-

import logging
import time

import requests

from .constants import BASE_URL

__all__ = [
    'OlsClient'
]

log = logging.getLogger(__name__)

api_ontology = '/api/ontologies/{ontology}'
api_terms = '/api/ontologies/{ontology}/terms'
api_term = '/api/ontologies/{ontology}/terms/{iri}'
api_properties = '/api/ontologies/{ontology}/properties/{iri}'
api_indivduals = '/api/ontologies/{ontology}/individuals/{iri}'
api_suggest = '/api/suggest'
api_search = '/api/search'


def _iterate_response_terms(response):
    """Iterates over the terms in the given response"""
    embedded = response['_embedded']

    terms = embedded['terms']

    for term in terms:
        yield term


class OlsClient:
    """Wraps the functions to query the Ontology Lookup Service such that alternative base URL's can be used."""

    def __init__(self, ols_base=None):
        """
        :param ols_base: An optional, custom URL for the OLS RESTful API.
        """
        self.base = (ols_base if ols_base is not None else BASE_URL).rstrip('/')

        self.ontology_terms_fmt = self.base + api_terms
        self.ontology_metadata_fmt = self.base + api_ontology
        self.ontology_suggest = self.base + api_suggest
        self.ontology_search = self.base + api_search

    def search(self, name, query_fields=None):
        """Searches the OLS with the given term

        :param str name:
        :param list[str] query_fields: Fields to query
        :return: dict
        """
        params = {'q': name}
        if query_fields is not None:
            params['queryFields'] = '{{{}}}'.format(','.join(query_fields))
        response = requests.get(self.ontology_search, params=params)
        return response.json()

    def suggest(self, name, ontology=None):
        """Suggest terms from an optional list of ontologies

        :param str name:
        :param list[str] ontology:
        :rtype: dict

        .. seealso:: https://www.ebi.ac.uk/ols/docs/api#_suggest_term
        """
        params = {'q': name}
        if ontology:
            params['ontology'] = ','.join(ontology)
        response = requests.get(self.ontology_suggest, params=params)
        return response.json()

    def iter_terms(self, ontology, size=None, sleep=None):
        """Iterates over all terms, lazily with paging

        :param str ontology: The name of the ontology
        :param int size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param int sleep: The amount of time to sleep between pages. Defaults to none.
        """
        if size is None:
            size = 500
        elif size > 500:
            raise ValueError('Maximum size is 500. Given: {}'.format(size))

        url = self.ontology_terms_fmt.format(ontology=ontology)

        t = time.time()
        response = requests.get(url, params={'size': size}).json()
        links = response['_links']

        for response_term in _iterate_response_terms(response):
            yield response_term

        t = time.time() - t

        log.info(
            'Page %s/%s done in %.2f seconds',
            response['page']['number'],
            response['page']['totalPages'],
            t
        )

        log.info('Estimated time until done: %.2f minutes', t * response['page']['totalPages'] / 60)

        while 'next' in links:
            if sleep:
                time.sleep(sleep)

            t = time.time()
            response = requests.get(links['next']['href'], params={'size': size}).json()
            links = response['_links']

            for response_term in _iterate_response_terms(response):
                yield response_term

            log.info(
                'Page %s/%s done in %.2f seconds',
                response['page']['number'],
                response['page']['totalPages'],
                time.time() - t
            )

    def iter_labels(self, ontology, size=None):
        """Iterates over the labels of terms in the ontology. Automatically wraps the pager returned by the OLS.

        :param str ontology: The name of the ontology
        :param int size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :rtype: iter[str]
        """
        for term in self.iter_terms(ontology=ontology, size=size):
            yield term['label']

    def get_metadata(self, ontology):
        """Gets the metadata for a given ontology

        :param str ontology: The name of the ontology
        :return: The dictionary representing the JSON from the OLS
        :rtype: dict
        """
        url = self.ontology_metadata_fmt.format(ontology=ontology)
        response = requests.get(url).json()
        return response

    def get_description(self, ontology):
        """Gets the description of a given ontology

        :param str ontology: The name of the ontology
        :rtype: str
        """
        response = self.get_metadata(ontology=ontology)

        return response['config'].get('description')
