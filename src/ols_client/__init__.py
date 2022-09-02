# -*- coding: utf-8 -*-

"""A client to the EBI Ontology Lookup Service."""

from class_resolver import ClassResolver

from .client import Client, EBIClient, NFDI4ChemClient, NFDI4IngClient, TIBClient

__all__ = [
    "client_resolver",
    # Base class
    "Client",
    # Concrete classes
    "EBIClient",
    "TIBClient",
    "NFDI4IngClient",
    "NFDI4ChemClient",
]

client_resolver = ClassResolver.from_subclasses(Client)
