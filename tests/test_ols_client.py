# -*- coding: utf-8 -*-

"""Tests for the client."""

from ols_client.client import EBIClient, TIBClient
from tests import cases


class TestEBI(cases.TestClient):
    """Tests for the EBI client."""

    client_cls = EBIClient
    test_ontology = "aro"
    test_label = "tetracycline-resistant ribosomal protection protein"
    test_search_query = "Orbitrap Eclipse"
    test_iri = "sbo", "http://biomodels.net/SBO/SBO_0000150"


class TestTIB(cases.TestClient):
    """Tests for the TIB client."""

    client_cls = TIBClient
    test_ontology = "oeo"
    test_label = "electric vehicle"
    test_search_query = "electric vehicle"
