# -*- coding: utf-8 -*-

import sys

import click

from .api import get_labels


@click.command()
@click.argument('ontology')
@click.option('-o', '--output', type=click.File('r'), default=sys.stdout)
def main(ontology, output):
    """Output the names to the given file"""
    for x in get_labels(ontology_name=ontology):
        print(x, file=output)


if __name__ == '__main__':
    main()
