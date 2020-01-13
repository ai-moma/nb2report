# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys
import logging
import jinja2
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

from pathlib import Path
from nb2report.cell_utils import is_assert, is_markdown, is_code, get_output


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
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
    path: pathlib.PosixPath
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
    if path.stem[0] != '.' and path.is_dir():
        if path not in scaffold['dirs']:
            scaffold['dirs'][path] = {'dirs': {}, 'files': {}}

            if level > 0:
                _add_report(path.name, '', REPORTING_COLORS[level])

        [_explore_scaffolding(path / x, scaffold['dirs'][path], level + 1)
         for x in os.listdir(str(path))]
    elif path.suffix == '.ipynb':
        logger.debug('Add report %s' % path)
        _add_report(path.name, _execute_test(str(path)), REPORTING_COLORS[-1])

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
    """ Load the ipython notebook as a notebook node.

    Parameters
    ----------
    f: str
        Path to the schema file.

    Returns
    -------
    NotebookNode
        A json-like object representing the notebook file.
    """
    with open(f) as nb:
        notebook = nbformat.read(nb, as_version=4)

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
    logger.debug("Evaluating output: %s" % output)
    try:
        return eval(output.strip().lower().capitalize())
    except Exception as ex:
        logger.error(
            "Received string '{}' (lenght: {}) is not a binary output. Please "
            "check all assert cells return True or False"
            .format(output, len(output))
        )
        raise ex


def _evaluate_results(results):
    """ Evaluate resulting assertions.

    Evaluation is OK if all assertions are true, otherwise it is KO

    Parameters
    ----------
    results: list(bool)
        List with the assertion results.

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
        # load f as notebook node
        notebook = _load_notebook(f)

        # execute notebook inplace
        ep = ExecutePreprocessor(timeout=600)
        logger.debug('Executing notebook: \n%s' % f)
        ep.preprocess(notebook)

        # find starting cell index
        assert_cell_index = _get_assert_cell_index(notebook['cells'])
        logger.debug('Assert cell found at %s' % assert_cell_index)

        # execute all tests
        for test_cell in notebook['cells'][assert_cell_index + 1:]:
            if is_code(test_cell):
                res = get_output(test_cell)
                test_results.append(_evaluate_output(res))

    except Exception as ex:
        logger.error('Error executing notebook %s' % f)
        raise ex

    return _evaluate_results(test_results)


def generate_summary(framework_name, framework_version, debug_mode=False):
    """ Generate summary report for given framework and version.

    The report file will be generated at:

            ./framework_name/framework_version/REPORTING_FILE_NAME

    Parameters
    ----------
    framework_name: str
        Framework name.
    framework_version: str
        Framework version.
    debug_mode: bool
        Whether debug mode is activated or not. Default to False.
    """
    if debug_mode:
        logger.setLevel(logging.DEBUG)

    root_path = Path(os.getcwd()) / framework_name / framework_version
    reporting_path = root_path / REPORTING_FILE_NAME

    _explore_scaffolding(
        root_path,
        scaffold={'dirs': {}, 'files': {}}
    )

    loader = jinja2.FileSystemLoader(str(REPORTING_TEMPLATE))
    env = jinja2.Environment(loader=loader)
    template = env.get_template('')

    with open(str(reporting_path), 'w') as f:
        f.writelines(template.render(dict(
            title='Test summary for {} {}'.format(
                framework_name,
                framework_version
            ),
            report=REPORTING_ITEMS
        )))

    logger.info("Summary report generated successfully at %s" % reporting_path)
    # Once the summary is generated, item list can be reseted
    REPORTING_ITEMS.clear()
