# -*- coding: utf-8 -*-

"""Tests for the client."""

import unittest
from typing import ClassVar, Optional, Tuple, Type

from ols_client.client import Client

__all__ = [
    "TestClient",
]


class TestClient(unittest.TestCase):
    """Test the OLS client."""

    client_cls: ClassVar[Type[Client]]
    test_ontology: ClassVar[str]
    test_label: ClassVar[str]
    test_search_query: ClassVar[Optional[str]] = None
    test_iri: ClassVar[Optional[Tuple[str, str]]] = None

    def setUp(self) -> None:
        """Set up the test case."""
        self.client = self.client_cls()

    def test_iter_labels(self):
        """Test getting labels."""
        labels = set(self.client.iter_labels(self.test_ontology))
        self.assertIn(self.test_label, labels, msg=f"\n\nGot {len(labels)} labels")

    def test_search(self):
        """Test search."""
        if not self.test_search_query:
            self.skipTest("no test query given")
        self.client.search(self.test_search_query)

    def test_get_term(self):
        """Test getting a term."""
        if not self.test_iri:
            self.skipTest("no test IRI given")
        ontology, iri = self.test_iri
        res_json = self.client.get_term(ontology, iri)
        terms = res_json["_embedded"]["terms"]
        self.assertEqual(1, len(terms))
        term = terms[0]
        self.assertEqual(iri, term["iri"])
