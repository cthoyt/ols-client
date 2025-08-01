# -*- coding: utf-8 -*-

"""Tests for the client."""

from ols_client.client import EBIClient
from tests import cases


class TestEbi(cases.TestClient):
    """Tests for the EBI client."""

    client_cls = EBIClient
    test_ontology = "aro"
    test_label = "tetracycline-resistant ribosomal protection protein"

    def test_get_term(self):
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
