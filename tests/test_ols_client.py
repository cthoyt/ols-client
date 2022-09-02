# -*- coding: utf-8 -*-

"""Tests for the client."""

import unittest

from ols_client.client import EBIClient


class TestClient(unittest.TestCase):
    """Test the OLS client."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.client = EBIClient()

    def test_iter_labels(self):
        """Test getting labels."""
        labels = set(self.client.iter_labels("aro"))
        self.assertIn("process or component of antibiotic biology or chemistry", labels)
