# -*- coding: utf-8 -*-

"""Client classes for the OLS."""

import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import requests

__all__ = [
    # Base client
    "Client",
    # Concrete
    "OlsClient",
    "TIBClient",
    "NFDI4ChemClient",
    "NFDI4IngClient",
]

logger = logging.getLogger(__name__)

HIERARCHICAL_CHILDREN = "hierarchicalChildren"

api_ontology = "/api/ontologies/{ontology}"
api_terms = "/api/ontologies/{ontology}/terms"
api_term = "/api/ontologies/{ontology}/terms/{iri}"
api_properties = "/api/ontologies/{ontology}/properties/{iri}"
api_indivduals = "/api/ontologies/{ontology}/individuals/{iri}"
api_suggest = "/api/suggest"
api_search = "/api/search"
api_descendants = "/api/ontologies/{ontology}/terms/{iri}/hierarchicalDescendants"


def _iterate_response_terms(response):
    """Iterate over the terms in the given response."""
    for term in response["_embedded"]["terms"]:
        yield term


def _help_iterate_labels(term_iterator):
    for term in term_iterator:
        yield term["label"]


class Client:
    """Wraps the functions to query the Ontology Lookup Service such that alternative base URL's can be used."""

    def __init__(self, base_url: str):
        """Initialize the client.

        :param base_url: An optional, custom URL for the OLS RESTful API.
        """
        self.base_url = base_url.rstrip("/")

        self.ontology_terms_fmt = self.base_url + api_terms
        self.ontology_term_fmt = self.base_url + api_term
        self.ontology_metadata_fmt = self.base_url + api_ontology
        self.ontology_suggest = self.base_url + api_suggest
        self.ontology_search = self.base_url + api_search
        self.ontology_term_descendants_fmt = self.base_url + api_descendants

    def get_json(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True,
        **kwargs,
    ):
        """Get the response JSON."""
        return self.get_response(
            path=path, params=params, raise_for_status=raise_for_status, **kwargs
        ).json()

    def get_response(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raise_for_status: bool = True,
        **kwargs,
    ) -> requests.Response:
        """Send a GET request the given endpoint.

        :param path: The path to query following the base URL, e.g., ``/ontologies``.
            If this starts with the base URL, it gets stripped.
        :param params: Parameters to pass through to :func:`requests.get`
        :param raise_for_status: If true and the status code isn't 200, raise an exception
        :param kwargs: Keyword arguments to pass through to :func:`requests.get`
        :returns: The response from :func:`requests.get`
        """
        if not params:
            params = {}
        if path.startswith(self.base_url):
            path = path[len(self.base_url) :]
        res = requests.get(self.base_url + "/" + path.lstrip("/"), params=params, **kwargs)
        if raise_for_status:
            res.raise_for_status()
        return res

    def get_ontology(self, ontology: str):
        """Get the metadata for a given ontology.

        :param ontology: The name of the ontology
        :return: The dictionary representing the JSON from the OLS
        :returns: Results about the ontology
        """
        return self.get_json(self.ontology_metadata_fmt.format(ontology=ontology))

    def get_term(self, ontology: str, iri: str):
        """Get the data for a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :returns: Results about the term
        """
        return self.get_json(self.ontology_term_fmt.format(ontology, iri))

    def search(self, query: str, query_fields: Optional[List[str]] = None):
        """Search the OLS with the given term.

        :param query: The query to search
        :param query_fields: Fields to query
        :return: dict
        :returns: A list of search results
        """
        params = {"q": query}
        if query_fields is not None:
            params["queryFields"] = "{{{}}}".format(",".join(query_fields))
        return self.get_json(self.ontology_search, params=params)

    def suggest(self, query: str, ontology: Union[None, str, List[str]] = None):
        """Suggest terms from an optional list of ontologies.

        :param query: The query to suggest
        :param ontology: The ontology or list of ontologies
        :returns: A list of suggestion results

        .. seealso:: https://www.ebi.ac.uk/ols/docs/api#_suggest_term
        """
        params = {"q": query}
        if ontology:
            params["ontology"] = ",".join(ontology) if isinstance(ontology, list) else ontology
        return self.get_json(self.ontology_suggest, params=params)

    @staticmethod
    def _iter_terms_helper(url: str, size: Optional[int] = None, sleep: Optional[int] = None):
        """Iterate over all terms, lazily with paging.

        :param url: The url to query
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to none.
        :rtype: iter[dict]
        :yields: A terms in an ontology
        :raises ValueError: if an invalid size is given
        """
        if size is None:
            size = 500
        elif size > 500:
            raise ValueError("Maximum size is 500. Given: {}".format(size))

        t = time.time()
        response = requests.get(url, params={"size": size}).json()
        links = response["_links"]

        for response_term in _iterate_response_terms(response):
            yield response_term

        t = time.time() - t

        logger.info(
            "Page %s/%s done in %.2f seconds",
            response["page"]["number"] + 1,
            response["page"]["totalPages"],
            t,
        )

        logger.info(
            "Estimated time until done: %.2f minutes", t * response["page"]["totalPages"] / 60
        )

        while "next" in links:
            if sleep:
                time.sleep(sleep)

            t = time.time()
            response = requests.get(links["next"]["href"], params={"size": size}).json()
            links = response["_links"]

            yield from _iterate_response_terms(response)

            logger.info(
                "Page %s/%s done in %.2f seconds",
                response["page"]["number"],
                response["page"]["totalPages"],
                time.time() - t,
            )

    def iter_terms(self, ontology: str, size: Optional[int] = None, sleep: Optional[int] = None):
        """Iterate over all terms, lazily with paging.

        :param ontology: The name of the ontology
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :rtype: iter[dict]
        :yields: Terms in the ontology
        """
        url = self.ontology_terms_fmt.format(ontology=ontology)
        yield from self._iter_terms_helper(url, size=size, sleep=sleep)

    def iter_descendants(
        self,
        ontology: str,
        iri: str,
        size: Optional[int] = None,
        sleep: Optional[int] = None,
    ):
        """Iterate over the descendants of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :rtype: iter[dict]
        :yields: the descendants of the given term
        """
        url = self.ontology_term_descendants_fmt.format(ontology=ontology, iri=iri)
        logger.info("getting %s", url)
        yield from self._iter_terms_helper(url, size=size, sleep=sleep)

    def iter_descendants_labels(
        self, ontology: str, iri: str, size: Optional[int] = None, sleep: Optional[int] = None
    ) -> Iterable[str]:
        """Iterate over the labels for the descendants of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: labels of the descendants of the given term
        """
        yield from _help_iterate_labels(
            self.iter_descendants(ontology, iri, size=size, sleep=sleep)
        )

    def iter_labels(
        self, ontology: str, size: Optional[int] = None, sleep: Optional[int] = None
    ) -> Iterable[str]:
        """Iterate over the labels of terms in the ontology. Automatically wraps the pager returned by the OLS.

        :param ontology: The name of the ontology
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: labels of terms in the ontology
        """
        yield from _help_iterate_labels(self.iter_terms(ontology=ontology, size=size, sleep=sleep))

    def iter_hierarchy(
        self, ontology: str, size: Optional[int] = None, sleep: Optional[int] = None
    ) -> Iterable[Tuple[str, str]]:
        """Iterate over parent-child relation labels.

        :param ontology: The name of the ontology
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: pairs of parent/child labels
        """
        for term in self.iter_terms(ontology=ontology, size=size, sleep=sleep):
            try:
                hierarchy_children_link = term["_links"][HIERARCHICAL_CHILDREN]["href"]
            except KeyError:  # there's no children for this one
                continue

            response = requests.get(hierarchy_children_link).json()

            for child_term in response["_embedded"]["terms"]:
                yield term["label"], child_term["label"]  # TODO handle different relation types

    def get_description(self, ontology: str) -> Optional[str]:
        """Get the description of a given ontology.

        :param ontology: The name of the ontology
        :returns: The description of the ontology.
        """
        response = self.get_ontology(ontology)
        return response["config"].get("description")


class OlsClient(Client):
    """The first-party instance of the OLS.

    .. seealso:: http://www.ebi.ac.uk/ols
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="http://www.ebi.ac.uk/ols")


class TIBClient(Client):
    """The TIB instance of the OLS.

    With its new Terminology Service, TIB – Leibniz Information Centre
    for Science and Technology and University Library provides a single
    point of access to terminology from domains such as architecture,
    chemistry, computer science, mathematics and physics.

    .. seealso:: https://service.tib.eu/ts4tib/
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://service.tib.eu/ts4tib/")


class NFDI4IngClient(Client):
    """The NFDI4Ing instance of the OLS.

    NFDI4Ing Terminology Service is a repository for engineering
    ontologies that aims to provide a single point of access to
    the latest ontology versions.

    .. seealso:: https://service.tib.eu/ts4ing/index
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://service.tib.eu/ts4ing/index")


class NFDI4ChemClient(Client):
    """The NFDI4Chem instance of the OLS.

    The NFDI4Chem Terminology Service is a repository for chemistry
    and related ontologies providing a single point of access to the
    latest ontology versions.

    .. seealso:: https://terminology.nfdi4chem.de/ts/
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://terminology.nfdi4chem.de/ts/")
