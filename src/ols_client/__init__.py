# -*- coding: utf-8 -*-

"""A client to the EBI Ontology Lookup Service."""

from class_resolver import ClassResolver

from .client import (
    Client,
    EBIClient,
    FraunhoferClient,
    MonarchClient,
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
    "ZBMedClient",
    "FraunhoferClient",
    "MonarchClient",
]

client_resolver = ClassResolver.from_subclasses(Client)
