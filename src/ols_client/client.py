# -*- coding: utf-8 -*-

"""Client classes for the OLS."""

import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import quote

import requests

__all__ = [
    # Base client
    "Client",
    # Concrete
    "EBIClient",
    "TIBClient",
    "NFDI4ChemClient",
    "NFDI4IngClient",
    "ZBMedClient",
    "MonarchClient",
    "FraunhoferClient",
]

logger = logging.getLogger(__name__)


def _iterate_response_terms(response):
    """Iterate over the terms in the given response."""
    yield from response["_embedded"]["terms"]


def _quote(iri):
    # must be double encoded https://www.ebi.ac.uk/ols/docs/api
    iri = quote(iri, safe="")
    iri = quote(iri, safe="")
    return iri


def _help_iterate_labels(term_iterator):
    for term in term_iterator:
        yield term["label"]


class Client:
    """Wraps the functions to query the Ontology Lookup Service such that alternative base URL's can be used."""

    def __init__(self, base_url: str):
        """Initialize the client.

        :param base_url: An optional, custom URL for the OLS API.
        """
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/api"):
            base_url = f"{base_url}/api"
        self.base_url = base_url

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
        url = self.base_url + "/" + path.lstrip("/")
        res = requests.get(url, params=params, **kwargs)
        if raise_for_status:
            res.raise_for_status()
        return res

    def get_paged(
        self,
        path: str,
        key: Optional[str] = None,
        size: Optional[int] = None,
        sleep: Optional[int] = None,
    ) -> Iterable:
        """Iterate over all terms, lazily with paging.

        :param path: The url to query
        :param key: The key to slice from the _embedded field
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to none.
        :yields: A terms in an ontology
        :raises ValueError: if an invalid size is given
        """
        if size is None:
            size = 500
        elif size > 500:
            raise ValueError(f"Maximum size is 500. Given: {size}")

        res_json = self.get_json(path, params={"size": size})
        yv = res_json["_embedded"]
        if key:
            yv = yv[key]
        yield from yv
        next_href = (res_json.get("_links") or {}).get("href")
        while next_href:
            if sleep is not None:
                time.sleep(sleep)
            loop_res_json = requests.get(next_href).json()
            yv = loop_res_json["_embedded"]
            if key:
                yv = yv[key]
            yield from yv
            next_href = (loop_res_json.get("_links") or {}).get("href")

    def get_ontologies(self):
        """Get all ontologies."""
        return self.get_paged("/ontologies", key="ontologies")

    def get_ontology(self, ontology: str):
        """Get the metadata for a given ontology.

        :param ontology: The name of the ontology
        :return: The dictionary representing the JSON from the OLS
        """
        return self.get_json(f"/ontologies/{ontology}")

    def get_term(self, ontology: str, iri: str):
        """Get the data for a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :returns: Results about the term
        """
        return self.get_json(f"/ontologies/{ontology}/terms", params={"iri": iri})

    def search(self, query: str, query_fields: Optional[Iterable[str]] = None, params=None):
        """Search the OLS with the given term.

        :param query: The query to search
        :param query_fields: Fields to query
        :param params: Additional params to pass through to :func:`get_json`
        :return: dict
        :returns: A list of search results
        """
        params = dict(params or {})
        params["q"] = query
        if query_fields:
            params["queryFields"] = ",".join(query_fields)
        return self.get_json("/search", params=params)["response"]["docs"]

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
        return self.get_json("/suggest", params=params)

    def iter_terms(self, ontology: str, size: Optional[int] = None, sleep: Optional[int] = None):
        """Iterate over all terms, lazily with paging.

        :param ontology: The name of the ontology
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :rtype: iter[dict]
        :yields: Terms in the ontology
        """
        yield from self.get_paged(
            f"/ontologies/{ontology}/terms", key="terms", size=size, sleep=sleep
        )

    def iter_ancestors(
        self,
        ontology: str,
        iri: str,
        size: Optional[int] = None,
        sleep: Optional[int] = None,
    ):
        """Iterate over the ancestors of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :rtype: iter[dict]
        :yields: the descendants of the given term
        """
        yield from self.get_paged(
            f"ontologies/{ontology}/terms/{_quote(iri)}/ancestors",
            key="terms",
            size=size,
            sleep=sleep,
        )

    def iter_hierarchical_ancestors(
        self,
        ontology: str,
        iri: str,
        size: Optional[int] = None,
        sleep: Optional[int] = None,
    ):
        """Iterate over the hierarchical of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :rtype: iter[dict]
        :yields: the descendants of the given term
        """
        yield from self.get_paged(
            f"ontologies/{ontology}/terms/{_quote(iri)}/hierarchicalAncestors",
            key="terms",
            size=size,
            sleep=sleep,
        )

    def iter_ancestors_labels(
        self, ontology: str, iri: str, size: Optional[int] = None, sleep: Optional[int] = None
    ) -> Iterable[str]:
        """Iterate over the labels for the descendants of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size: The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: labels of the descendants of the given term
        """
        yield from _help_iterate_labels(self.iter_ancestors(ontology, iri, size=size, sleep=sleep))

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
                hierarchy_children_link = term["_links"]["hierarchicalChildren"]["href"]
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


class EBIClient(Client):
    """The first-party instance of the OLS.

    .. seealso:: https://www.ebi.ac.uk/ols4
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://www.ebi.ac.uk/ols4")


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
        super().__init__(base_url="https://service.tib.eu/ts4tib")


class NFDI4IngClient(Client):
    """The NFDI4Ing instance of the OLS.

    NFDI4Ing Terminology Service is a repository for engineering
    ontologies that aims to provide a single point of access to
    the latest ontology versions.

    .. seealso:: https://service.tib.eu/ts4ing/index
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://service.tib.eu/ts4ing")


class NFDI4ChemClient(Client):
    """The NFDI4Chem instance of the OLS.

    The NFDI4Chem Terminology Service is a repository for chemistry
    and related ontologies providing a single point of access to the
    latest ontology versions.

    .. seealso:: https://terminology.nfdi4chem.de/ts/
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://terminology.nfdi4chem.de/ts")


class ZBMedClient(Client):
    """The ZB Med instance of the OLS.

    .. seealso:: https://semanticlookup.zbmed.de/ols
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://semanticlookup.zbmed.de/ols")


class MonarchClient(Client):
    """The Monarch Initiative instance of the OLS.

    .. seealso:: https://ols.monarchinitiative.org/
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://ols.monarchinitiative.org/")


class FraunhoferClient(Client):
    """The Fraunhofer SCAI instance of the OLS.

    .. warning:: Fraunhofer SCAI resources are typically not maintained, do not rely on this.

    .. seealso:: https://rohan.scai.fraunhofer.de
    """

    def __init__(self):
        """Initialize the client."""
        super().__init__(base_url="https://rohan.scai.fraunhofer.de")
