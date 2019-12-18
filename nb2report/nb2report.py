import os
import click

import nb2report.scaffolding as scaffolding
import nb2report.reporting as reporting


@click.group()
def cli():
    """"This is nb2convert a tool to generate the necessary scaffolding and
    execution of notebooks to generate a report in html"""
    pass


@cli.command()
@click.option('-n', '--name', help='Framework name')
@click.option('-v', '--version', help='Framework version')
@click.option(
    '-i',
    '--input',
    help='Path to the notebook with the test schema')
def create_scaffolding(name, version, input):
    """Creates the scaffolding of a specific framework following the
    test schema specified in a notebook using markdown"""
    schema_path = os.path.abspath(input)
    scaffolding.create(name, version, schema_path)


@cli.command()
@click.option('-n', '--name', help='Framework name')
@click.option('-v', '--version', help='Framework version')
def create_report(name, version):
    """Creates the html report by executing the notebooks contained
    inside the framework name and version folders"""
    reporting.generate_summary(name, version)
