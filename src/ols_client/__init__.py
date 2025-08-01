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
    # Base class
    "Client",
    # Concrete classes
    "EBIClient",
    "FraunhoferClient",
    "MonarchClient",
    "TIBClient",
    "ZBMedClient",
    "client_resolver",
]

client_resolver = ClassResolver.from_subclasses(Client)
