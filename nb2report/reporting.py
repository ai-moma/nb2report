# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import re
import os
import json
import sys
import logging
import jinja2

from pathlib import Path
from nb2report.cell_utils import is_assert, is_markdown, is_code, get_code

from IPython.testing.globalipapp import get_ipython
from IPython.utils.io import capture_output


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)  # ToDo: INFO
logger = logging.getLogger('nb2report')

IPYTHON_INTERPRETER = None
BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
CONFIG_DIR = BASE_DIR / '.config'
REPORTING_FILE_NAME = "summary.html"
REPORTING_TEMPLATE = CONFIG_DIR / "report_template.html"
REPORTING_ITEMS = []
REPORTING_COLORS = [
    'Teal',
    'DarkCyan',
    'LightSeaGreen',
    'DarkSeaGreen',
    'MediumAquamarine'
]


def _explore_scaffolding(path, scaffold, level=0):
    """ Explore the scaffolding based on given root path.

    Parameters
    ----------
    path: str
        Absolute path to explore.
    scaffold: dict
        Currently explored scaffold.
    level: int
        Depth level of current exploration.

    Returns
    -------
    dict
        Explored scaffold.
    """
    if os.path.isdir(path):
        if path not in scaffold['dirs']:
            scaffold['dirs'][path] = {'dirs': {}, 'files': {}}

            if level > 0:
                _add_report(path.name, '', REPORTING_COLORS[level])

        [_explore_scaffolding(path / x, scaffold['dirs'][path], level + 1)
         for x in os.listdir(path)]
    elif Path(path).suffix == 'ipynb':
        logger.debug('Add report %s' % path)
        _add_report(path.name, _execute_test(path), REPORTING_COLORS[-1])

    return scaffold


def _add_report(title, result, color):
    """ Add reporting item in required format.

    Parameters
    ----------
    title: str
        Reporting title.
    result: str
        Test result. It is OK, KO or empty (at title/subtitle items)
    color: str
        Name of css color for this item.
    """
    if result == 'OK':
        supported_color = 'green'
    else:
        supported_color = 'red'

    REPORTING_ITEMS.append(dict(
        title=title,
        color=color,
        supported=result,
        supported_color=supported_color
    ))


def _load_notebook(f):
    """ Load the ipython notebook as a dict.

    Parameters
    ----------
    f: str
        Path to the schema file.

    Returns
    -------
    dict
        json string representing the notebook file.
    """
    with open(f, 'r') as json_file:
        notebook = json.load(json_file)

    return notebook


def _get_assert_cell_index(cells):
    """ Get the index where assertion cells start.

    There is a marked cell where assertions start.
    Further cells will contain only tests which should return all True.

    Parameters
    ----------
    cells: list(dict)
        List of all notebook cells.

    Returns
    -------
    int
        Assert cell index.
    """
    asserts_cell = list(filter(
        lambda x: is_markdown(x[1]) and is_assert(x[1]),
        enumerate(cells)
    ))

    if not asserts_cell:
        raise LookupError('Asserts cell cannot be found')

    return asserts_cell[0][0]


def _clean_output(s):
    """ Clean the cell execution output.

    Executed cells will return some string like "Out[1]: True"

    >>> _clean_output("Out[1]: True")
    True

    Parameters
    ----------
    s: str
        Cell execution output.

    Returns
    -------
    str
        Cleaned cell execution output.
    """
    return re.sub(r'[a-zA-Z]+\[[0-9]+\]: +', '', s).replace('\n', '').strip()


def _get_interpreter():
    """ Get iPython interpreter.

    If it has been previously initialized, return it. Otherwise, start it.

    Further work: implement some mechanism to get an interpreter configured
    with some virtual environment or kernel.

    Returns
    -------
    callable
        iPython interpreter.
    """
    if not globals()['IPYTHON_INTERPRETER']:
        globals()['IPYTHON_INTERPRETER'] = get_ipython()

    return IPYTHON_INTERPRETER


def _run_cell(cmd):
    """ Execute some code using iPython interpreter.

    Parameters
    ----------
    cmd: str
        Code to execute.

    Returns
    -------
    str
        Cleaned code execution output.
    """
    with capture_output() as io:
        _get_interpreter().run_cell(cmd)
    res_out = io.stdout
    return _clean_output(res_out)


def _evaluate_output(output):
    """ Evaluate output string.

    Output must be a true or false string. Try to cast the str to a bool value.

    Parameters
    ----------
    output: str
        Output string

    Returns
    -------
    bool
        Casted output.
    """
    try:
        return eval(output.lower().capitalize())
    except Exception as ex:
        logger.error(
            'Received string %s is not a binary output. Please check all '
            'assert cells return True or False' % output
        )
        raise ex


def _evaluate_results(results):
    """ Evaluate resulting assertions.

    Evaluation is OK if all assertions are true, otherwise it is KO

    Parameters
    ----------
    results: list(bool)
        List of all assertion execution results.

    Returns
    -------
    str
        'OK' if all assertions are true, 'KO' otherwise
    """
    if len(results) and results.count(True) == len(results):  # all True
        return 'OK'
    else:
        return 'KO'


def _execute_test(f):
    """ Execute some test notebook file.

    There is a cell called "# Asserts" where tests start. All cells on are
    asserts that must be true.

    Parameters
    ----------
    f: str
        Path to the notebook file.

    Returns
    -------
    str
        Test result. 'OK' if all cells returned True, 'KO' otherwise.
    """
    test_results = []

    try:
        # load f as a dict
        notebook = _load_notebook(f)
        # find starting cell index
        assert_cell_index = _get_assert_cell_index(notebook['cells'])
        logger.debug('Assert cell found at %s' % assert_cell_index)

        # execute all tests
        for test_cell in notebook['cells'][assert_cell_index + 1:]:
            if is_code(test_cell):
                code = get_code(test_cell)
                logger.debug('Executing code:\n%s' % code)
                test_results.append(_evaluate_output(_run_cell(code)))

    except Exception as ex:
        logger.error('Error executing notebook %s' % f)
        raise ex

    return _evaluate_results(test_results)


def generate_summary(framework_name, framework_version):
    """ Generate summary report for given framework and version.

    The report file will be generated at:

            ./framework_name/framework_version/REPORTING_FILE_NAME

    Parameters
    ----------
    framework_name: str
        Framework name.
    framework_version: str
        Framework version.
    """
    test_root_path = BASE_DIR / framework_name / framework_version
    reporting_path = test_root_path / REPORTING_FILE_NAME

    _explore_scaffolding(
        test_root_path,
        scaffold={'dirs': {}, 'files': {}}
    )

    loader = jinja2.FileSystemLoader(str(REPORTING_TEMPLATE))
    env = jinja2.Environment(loader=loader)
    template = env.get_template('')

    with open(reporting_path, 'w') as f:
        f.writelines(template.render(dict(
            title='Test summary for {} {}'.format(
                framework_name,
                framework_version
            ),
            report=REPORTING_ITEMS
        )))

    logger.info("Summary report generated successfully at %s" % reporting_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='Execute some framework tests')
    parser.add_argument("-n", '--name',
                        required=True,
                        help='Name of the new framework to tests.')

    parser.add_argument("-v", '--version',
                        required=True,
                        help='Version of the framework to tests.')

    args = parser.parse_args(sys.argv[1:])

    f_name = args.name
    f_version = args.version

    generate_summary(f_name, f_version)
