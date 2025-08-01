"""Tests for the client."""

import unittest

from ols_client import EBIClient


class TestEbi(unittest.TestCase):
    """Tests for the EBI client."""

    test_ontology = "duo"
    test_label = "compiling software"

    def setUp(self) -> None:
        """Set up the test case."""
        self.client = EBIClient()

    def test_iter_labels(self) -> None:
        """Test getting labels."""
        labels = set(self.client.iter_labels(self.test_ontology))
        self.assertIn(self.test_label, labels)

    def test_get_term(self) -> None:
        """Test getting a term."""
        iri = "http://biomodels.net/SBO/SBO_0000150"
        res_json = self.client.get_term("sbo", iri)
        terms = res_json["_embedded"]["terms"]
        self.assertEqual(1, len(terms))
        term = terms[0]
        self.assertEqual(iri, term["iri"])

    def test_get_embedding(self) -> None:
        """Test getting an embedding."""
        e = self.client.get_embedding("obi", "http://purl.obolibrary.org/obo/OBI_0003699")
        self.assertIsInstance(e, list)
        self.assertTrue(all(isinstance(v, float) for v in e))
