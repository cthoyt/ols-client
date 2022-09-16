# -*- coding: utf-8 -*-

"""A client to the EBI Ontology Lookup Service."""

from class_resolver import ClassResolver

from .client import (
    Client,
    EBIClient,
    FraunhoferClient,
    MonarchClient,
    NFDI4ChemClient,
    NFDI4IngClient,
    TIBClient,
    ZBMedClient,
)

__all__ = [
    "client_resolver",
    # Base class
    "Client",
    # Concrete classes
    "EBIClient",
    "TIBClient",
    "NFDI4IngClient",
    "NFDI4ChemClient",
    "ZBMedClient",
    "FraunhoferClient",
    "MonarchClient",
]

client_resolver = ClassResolver.from_subclasses(Client)
