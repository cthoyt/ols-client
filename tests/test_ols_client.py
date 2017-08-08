# -*- coding: utf-8 -*-


import unittest

from ols_client import get_labels, get_metadata


class TestClient(unittest.TestCase):
    def test_terms(self):
        """Tests that the right terms are acquired.

        Uses the ``ancestro`` ontology because it's pretty short"""
        labels = set(get_labels('ancestro'))
        self.assertIn('Irish', labels)

    def test_metadata(self):
        """Tests that the right metadata are acquired."""
        metadata = get_metadata('ancestro')

        self.assertIn('numberOfTerms', metadata)
        self.assertEqual(540, metadata['numberOfTerms'])

        self.assertIn('config', metadata)
        self.assertIn('title', metadata['config'])
        self.assertIn('Ancestry Ontology', metadata['config']['title'])
