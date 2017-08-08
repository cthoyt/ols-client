# -*- coding: utf-8 -*-


import click

from .api import get_labels
from .constants import OLS_BASE, write_config, get_config


@click.group()
def main():
    """OLS Client Command Line Interface"""


@main.command()
@click.argument('ontology')
@click.option('-o', '--output', type=click.File('r'))
@click.option('-b', '--ols-base', help="OLS base url. Defaults to {}".format(OLS_BASE))
def labels(ontology, output, ols_base):
    """Output the names to the given file"""
    for label in get_labels(ontology_name=ontology, ols_base=ols_base):
        click.echo(label, file=output)


@main.command()
@click.argument('base')
def set_base(base):
    """Sets the default OLS base url"""
    config = get_config()
    config['BASE'] = base
    write_config(config)


if __name__ == '__main__':
    main()
