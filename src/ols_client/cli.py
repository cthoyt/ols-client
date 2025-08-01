"""CLI for the OLS client."""

import sys
from collections.abc import Iterable

import click

from .client import Client


@click.group()
def main() -> None:
    """Run the OLS Client Command Line Interface."""


ontology_argument = click.argument("ontology")
iri_option = click.option("--iri", required=True)
output_option = click.option("-o", "--output", type=click.File("w"), default=sys.stdout)
base_url_option = click.option(
    "-b", "--base-url", default="http://www.ebi.ac.uk/ols", show_default=True
)


def _echo_via_pager(x: Iterable[str]) -> None:
    click.echo_via_pager(term + "\n" for term in x)


@main.command()
@ontology_argument
@base_url_option
def labels(ontology: str, base_url: str) -> None:
    """Output the names to the given file."""
    client = Client(base_url)
    _echo_via_pager(client.iter_labels(ontology))


@main.command()
@ontology_argument
@iri_option
@base_url_option
def ancestors(ontology: str, iri: str, base_url: str) -> None:
    """Output the ancestors of the given term."""
    client = Client(base_url)
    _echo_via_pager(client.iter_ancestors_labels(ontology=ontology, iri=iri))


@main.command()
@click.argument("query")
@base_url_option
def search(query: str, base_url: str) -> None:
    """Search the OLS with the given query."""
    client = Client(base_url)
    _echo_via_pager(client.search(query=query))


@main.command()
@click.argument("query")
@click.option("--ontology")
@base_url_option
def suggest(query: str, ontology: str | None, base_url: str) -> None:
    """Suggest a term based on th given query."""
    client = Client(base_url)
    click.echo_via_pager(term + "\n" for term in client.suggest(query=query, ontology=ontology))


if __name__ == "__main__":
    main()
