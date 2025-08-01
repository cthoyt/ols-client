"""Tests for the client."""

import unittest
from typing import ClassVar

from ols_client.client import Client

__all__ = [
    "TestClient",
]


class TestClient(unittest.TestCase):
    """Test the OLS client."""

    client_cls: ClassVar[type[Client]]
    test_ontology: ClassVar[str]
    test_label: ClassVar[str]

    def setUp(self) -> None:
        """Set up the test case."""
        self.client = self.client_cls()  # type:ignore

    def test_iter_labels(self) -> None:
        """Test getting labels."""
        labels = set(self.client.iter_labels(self.test_ontology))
        self.assertIn(self.test_label, labels)
