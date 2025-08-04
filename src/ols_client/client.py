"""Client classes for the OLS."""

import logging
import time
from collections.abc import Iterable
from typing import Any, TypeAlias, cast
from urllib.parse import quote

import requests

__all__ = [
    # Base client
    "Client",
    # Concrete
    "EBIClient",
    "FraunhoferClient",
    "MonarchClient",
    "TIBClient",
    "ZBMedClient",
]

logger = logging.getLogger(__name__)


def _iterate_response_terms(response: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Iterate over the terms in the given response."""
    yield from response["_embedded"]["terms"]


def _quote(iri: str) -> str:
    # must be double encoded https://www.ebi.ac.uk/ols/docs/api
    iri = quote(iri, safe="")
    iri = quote(iri, safe="")
    return iri


def _help_iterate_labels(term_iterator: Iterable[dict[str, Any]]) -> Iterable[str]:
    for term in term_iterator:
        yield term["label"]


TimeoutHint: TypeAlias = float | int | None
Res: TypeAlias = Any


class Client:
    """A client for an OLS instance.

    It wraps the functions to query the OLS such that alternative base URLs can be used.
    """

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
        params: dict[str, Any] | None = None,
        raise_for_status: bool = True,
        timeout: TimeoutHint = None,
        **kwargs: Any,
    ) -> Res:
        """Get the response JSON."""
        return self.get_response(
            path=path, params=params, raise_for_status=raise_for_status, timeout=timeout, **kwargs
        ).json()

    def get_response(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        raise_for_status: bool = True,
        timeout: TimeoutHint = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a GET request the given endpoint.

        :param path: The path to query following the base URL, e.g., ``/ontologies``.
            If this starts with the base URL, it gets stripped.
        :param params: Parameters to pass through to :func:`requests.get`
        :param raise_for_status: If true and the status code isn't 200, raise an exception
        :param timeout: The timeout, defaults to 5 seconds if not given
        :param kwargs: Keyword arguments to pass through to :func:`requests.get`
        :returns: The response from :func:`requests.get`
        """
        if not params:
            params = {}
        if path.startswith(self.base_url):
            path = path[len(self.base_url) :]
        url = self.base_url + "/" + path.lstrip("/")
        res = requests.get(url, params=params, timeout=timeout or 5, **kwargs)
        if raise_for_status:
            res.raise_for_status()
        return res

    def get_paged(
        self,
        path: str,
        key: str | None = None,
        size: int | None = None,
        sleep: int | None = None,
        timeout: TimeoutHint = None,
    ) -> Iterable[dict[str, Any]]:
        """Iterate over all terms, lazily with paging.

        :param path: The url to query
        :param key: The key to slice from the _embedded field
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to none.
        :param timeout:
            The timeout, defaults to 5 seconds if not given.
            Applied both to initial request and each page
        :yields: A terms in an ontology
        :raises ValueError: if an invalid size is given
        """
        if size is None:
            size = 500
        elif size > 500:
            raise ValueError(f"Maximum size is 500. Given: {size}")

        res_json = self.get_json(path, timeout=timeout, params={"size": size})
        yv = res_json["_embedded"]
        if key:
            yv = yv[key]
        yield from yv
        next_href = (res_json.get("_links") or {}).get("href")
        while next_href:
            if sleep is not None:
                time.sleep(sleep)
            loop_res_json = requests.get(next_href, timeout=timeout).json()
            yv = loop_res_json["_embedded"]
            if key:
                yv = yv[key]
            yield from yv
            next_href = (loop_res_json.get("_links") or {}).get("href")

    def get_ontologies(self) -> Iterable[dict[str, Any]]:
        """Get all ontologies."""
        return self.get_paged("/ontologies", key="ontologies")

    def get_ontology(self, ontology: str) -> dict[str, Any]:
        """Get the metadata for a given ontology.

        :param ontology: The name of the ontology
        :return: The dictionary representing the JSON from the OLS
        """
        return cast(dict[str, Any], self.get_json(f"/ontologies/{ontology}"))

    def get_term(self, ontology: str, iri: str) -> dict[str, Any]:
        """Get the data for a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :returns: Results about the term
        """
        return cast(
            dict[str, Any], self.get_json(f"/ontologies/{ontology}/terms", params={"iri": iri})
        )

    def search(
        self,
        query: str,
        query_fields: Iterable[str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Res:
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

    def suggest(self, query: str, ontology: None | str | list[str] = None) -> Res:
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

    def iter_terms(
        self,
        ontology: str,
        size: int | None = None,
        sleep: int | None = None,
        timeout: TimeoutHint = None,
    ) -> Iterable[dict[str, Any]]:
        """Iterate over all terms, lazily with paging.

        :param ontology: The name of the ontology
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :param timeout: The timeout, defaults to 5 seconds if not given, applied to each page
        :yields: Terms in the ontology
        """
        yield from self.get_paged(
            f"/ontologies/{ontology}/terms", key="terms", size=size, sleep=sleep, timeout=timeout
        )

    def iter_ancestors(
        self,
        ontology: str,
        iri: str,
        size: int | None = None,
        sleep: int | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Iterate over the ancestors of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
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
        size: int | None = None,
        sleep: int | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Iterate over the hierarchical of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: the descendants of the given term
        """
        yield from self.get_paged(
            f"ontologies/{ontology}/terms/{_quote(iri)}/hierarchicalAncestors",
            key="terms",
            size=size,
            sleep=sleep,
        )

    def iter_ancestors_labels(
        self, ontology: str, iri: str, size: int | None = None, sleep: int | None = None
    ) -> Iterable[str]:
        """Iterate over the labels for the descendants of a given term.

        :param ontology: The name of the ontology
        :param iri: The IRI of a term
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: labels of the descendants of the given term
        """
        yield from _help_iterate_labels(self.iter_ancestors(ontology, iri, size=size, sleep=sleep))

    def iter_labels(
        self, ontology: str, size: int | None = None, sleep: int | None = None
    ) -> Iterable[str]:
        """Iterate over the labels of terms in the ontology.

        :param ontology: The name of the ontology
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :yields: labels of terms in the ontology

        This function automatically wraps the pager returned by the OLS.
        """
        yield from _help_iterate_labels(self.iter_terms(ontology=ontology, size=size, sleep=sleep))

    def iter_hierarchy(
        self,
        ontology: str,
        size: int | None = None,
        sleep: int | None = None,
        timeout: TimeoutHint = None,
    ) -> Iterable[tuple[str, str]]:
        """Iterate over parent-child relation labels.

        :param ontology: The name of the ontology
        :param size:
            The size of each page. Defaults to 500, which is the maximum allowed by the EBI.
        :param sleep: The amount of time to sleep between pages. Defaults to 0 seconds.
        :param timeout: The timeout, defaults to 5 seconds if not given
        :yields: pairs of parent/child labels
        """
        for term in self.iter_terms(ontology=ontology, size=size, sleep=sleep, timeout=timeout):
            try:
                hierarchy_children_link = term["_links"]["hierarchicalChildren"]["href"]
            except KeyError:  # there's no children for this one
                continue

            response = requests.get(hierarchy_children_link, timeout=timeout).json()

            for child_term in response["_embedded"]["terms"]:
                yield term["label"], child_term["label"]  # TODO handle different relation types

    def get_description(self, ontology: str) -> str | None:
        """Get the description of a given ontology.

        :param ontology: The name of the ontology
        :returns: The description of the ontology.
        """
        response = self.get_ontology(ontology)
        return cast(str | None, response["config"].get("description"))

    def get_embedding(self, ontology: str, iri: str) -> list[float]:
        """Get the text-based embedding for a term."""
        return cast(
            list[float],
            self.get_json(f"v2/ontologies/{ontology}/classes/{_quote(iri)}/llm_embedding"),
        )

    def get_embedding_similarity(
        self, ontology: str, iri: str, ontology_b: str, iri_b: str
    ) -> float:
        """Get cosine similarity between two entities' embeddings."""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        e1 = self.get_embedding(ontology, iri)
        e2 = self.get_embedding(ontology_b, iri_b)
        rv = cosine_similarity(np.array(e1).reshape(1, -1), np.array(e2).reshape(1, -1))
        return cast(float, rv[0][0].item())


class EBIClient(Client):
    """The first-party instance of the OLS.

    .. seealso:: https://www.ebi.ac.uk/ols4
    """

    def __init__(self) -> None:
        """Initialize the client."""
        super().__init__(base_url="https://www.ebi.ac.uk/ols4")


class TIBClient(Client):
    """The TIB instance of the OLS.

    With its new Terminology Service, TIB Leibniz Information Centre
    for Science and Technology and University Library provides a single
    point of access to terminology from domains such as architecture,
    chemistry, computer science, mathematics and physics.

    .. seealso:: https://service.tib.eu/ts4tib/
    """

    def __init__(self) -> None:
        """Initialize the client."""
        super().__init__(base_url="https://service.tib.eu/ts4tib")


class ZBMedClient(Client):
    """The ZB Med instance of the OLS.

    .. seealso:: https://semanticlookup.zbmed.de/ols
    """

    def __init__(self) -> None:
        """Initialize the client."""
        super().__init__(base_url="https://semanticlookup.zbmed.de/ols")


class MonarchClient(Client):
    """The Monarch Initiative instance of the OLS.

    .. seealso:: https://ols.monarchinitiative.org/
    """

    def __init__(self) -> None:
        """Initialize the client."""
        super().__init__(base_url="https://ols.monarchinitiative.org/")


class FraunhoferClient(Client):
    """The Fraunhofer SCAI instance of the OLS.

    .. warning:: Fraunhofer SCAI resources are typically not maintained, do not rely on this.

    .. seealso:: https://rohan.scai.fraunhofer.de
    """

    def __init__(self) -> None:
        """Initialize the client."""
        super().__init__(base_url="https://rohan.scai.fraunhofer.de")
