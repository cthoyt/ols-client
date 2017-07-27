# -*- coding: utf-8 -*-


import unittest

from ols_client import get_labels


class TestClient(unittest.TestCase):
    def test_terms(self):
        labels = set(get_labels('ancestro'))
        self.assertIn('Irish', labels)
