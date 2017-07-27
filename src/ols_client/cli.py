# -*- coding: utf-8 -*-


import click

from .api import get_labels, OLS_BASE


@click.group()
def main():
    """OLS Client Command Line Interface"""


@main.command()
@click.argument('ontology')
@click.option('-o', '--output', type=click.File('r'))
@click.option('-b', '--ols-base', help="OLS base url. Defaults to {}".format(OLS_BASE))
def names(ontology, output, ols_base):
    """Output the names to the given file"""
    for label in get_labels(ontology_name=ontology, ols_base=ols_base):
        click.echo(label, file=output)


if __name__ == '__main__':
    main()
