# -*- coding: utf-8 -*-

"""Tests for the client."""

import unittest
from typing import ClassVar, Type

from ols_client.client import Client

__all__ = [
    "TestClient",
]


class TestClient(unittest.TestCase):
    """Test the OLS client."""

    client_cls: ClassVar[Type[Client]]
    test_ontology: ClassVar[str]
    test_label: ClassVar[str]

    def setUp(self) -> None:
        """Set up the test case."""
        self.client = self.client_cls()

    def test_iter_labels(self):
        """Test getting labels."""
        labels = set(self.client.iter_labels(self.test_ontology))
        self.assertIn(self.test_label, labels)
