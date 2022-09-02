# -*- coding: utf-8 -*-

"""Tests for the client."""

from ols_client.client import EBIClient
from tests import cases


class TestEbi(cases.TestClient):
    """Tests for the EBI client."""

    client_cls = EBIClient
    test_ontology = "aro"
    test_label = "process or component of antibiotic biology or chemistry"
