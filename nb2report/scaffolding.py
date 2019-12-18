# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging
import os
import sys
import json
import re

from shutil import copyfile
from IPython.paths import get_ipython_dir
from pathlib import Path
from nb2report.cell_utils import is_list, is_title, get_first_line


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('nb2report')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IPYTHON_DIR = Path(get_ipython_dir())
TEMPLATE_NOTEBOOK_PATH = Path(BASE_DIR)\
                         / ".config"\
                         / "empty_notebook_template.ipynb"


def _load_schema(f):
    """ Load the ipynb markdown file describing the complete tests schema.

    Parameters
    ----------
    f: str
        Path to the schema file.

    Returns
    -------
    str
        json string representing the notebook file.
    """
    with open(f, 'r') as json_file:
        notebook = json.load(json_file)

    return notebook


def _setup_base_dir(framework, version):
    """ Create the root testing directory.

    All tests will be placed in this root directory.

    Parameters
    ----------
    framework: str
        Framework name.
    version: str
        Framework version.

    Returns
    -------
    Path: pathlib.PosixPath
        Complete path to the root testing directory.
    """
    framework_path = Path(os.getcwd()) / framework
    current_path = framework_path / version

    if not framework_path.exists():
        framework_path.mkdir()

    if not current_path.exists():
        current_path.mkdir()

    return current_path


def _walk_path(current_path, current_level, new_level, title):
    """ Explore the directory tree

    Parameters
    ----------
    current_path: str
        Path currently exploted.
    current_level: int
        Current depth level.
    new_level: int
        Next depth level. Level of the next iteration.
    title: str
        Title of the current path title.

    Returns
    -------
    str, str
        Path currently exploted
        Current depth level.
    """
    for i in range(abs(current_level - new_level) + 1):

        logger.debug(
            'Current path : {} - Current level: {} - New level: {} - i: {}'
            .format(current_path.name, current_level, new_level, i))

        if new_level > current_level:
            current_path = _level_in(current_path, title)
            current_level += 1
            logger.debug('Level IN: {}'.format(current_path.name))
        elif new_level < current_level:
            current_path = _level_out(current_path)
            current_level -= 1
            logger.debug('Level OUT: {}'.format(current_path.name))
        else:
            current_path = _level_out(current_path)
            current_path = _level_in(current_path, title)
            logger.debug('Level SAME: {}'.format(current_path.name))
            # current_level = same

    return current_path, current_level


def _get_new_level(first_line, current_level):
    """ Decide what is the next level based on current cell source.

    If current cell starts with a markdown title token #,
        then count the token apparitions in order to infer the subtitle level.
        The script will keep iterating over the next path.
    Else, if current cell starts with a list token *,
        then it is the end of this path, there is no longer titles nor
        subtitles. So next and last level at this path is current_level + 1

    Once the path exploration reaches a list (marked by * in markdown
    language), the next steps are just create a notebook for each list
    element. The tool will not look for further titles nor subtitles at this
    path.

    Parameters
    ----------
    first_line
    current_level

    Returns
    -------
    int, str
        Depth of the new level.
        Title of the new path.
    """
    if not first_line:
        return current_level, ''

    chunks = re.split(r'^(\*|#+)', first_line)
    if first_line[0] == '#':  # starts with a markdown title token: #
        new_level = len(chunks[1])  # count token apparitions
    else:  # starts with a list token: *
        new_level = current_level + 1  # it is the end of this path

    new_title = chunks[-1].strip()

    return new_level, new_title


def _generate_notebooks(enum_source, current_path):
    """ Generate a notebook for each item of the list.

    The new notebook is just a copy of the template _TEMPLATE_NOTEBOOK_PATH_

    Parameters
    ----------
    enum_source: list(str)
        List containing all notebook names to generate.
    current_path: pathlib.PosixPath
        Complete current path.
    """
    for item in enum_source:
        splitted = re.split(r'^ *\*+ +', item)  # remove list markdown token: *
        if len(splitted) > 1:  # if regex matched
            title = splitted[1].strip() + '.ipynb'
            copyfile(str(TEMPLATE_NOTEBOOK_PATH), str(current_path / title))


def _create_scaffolding(framework, version, cells):
    """ Create the testing scaffolding.

    Parameters
    ----------
    framework: str
        Framework name.
    version: str
        Framework version.
    cells: list(dict)
        List of all notebook cells.
    """
    current_level = 0
    current_path = _setup_base_dir(framework, version)

    for cell in cells:
        first_line = get_first_line(cell)

        if is_title(cell):
            new_level, title = _get_new_level(first_line, current_level)
            current_path, current_level = _walk_path(
                current_path,
                current_level,
                new_level,
                title
            )

        elif is_list(cell):
            _generate_notebooks(cell['source'], current_path)


def _level_in(current_path, new_title):
    """ Dive a level in.

    The actions to perform when diving a new level are:
        * Get the new path. It is composed by the current path + the new
        (sub)title.
        * Create the new path if it doesn't exist yet.
        * Return the new path.

    Parameters
    ----------
    current_path: pathlib.PosixPath
        Current absolute path.
    new_title: str
        Title of the new path.

    Returns
    -------
    str
        Next absolute path.
    """
    next_path = current_path / new_title
    logger.debug('Que cojones pasa')
    if not next_path.exists():
        logger.debug('Creating path %s' % next_path)
        next_path.mkdir()  # create new level

    return next_path


def _level_out(current_path):
    """ Get a level out.

    Parameters
    ----------
    current_path: pathlib.PosixPath
        Current absolute path.

    Returns
    -------
    str
        Next absolute path.
    """
    return current_path.parents[0]  # level back


def create(framework_name, framework_version, test_schema):
    """ Create the complete scaffolding.

    Given a framework name and version create the scaffolding following
    the test schema.

    Parameters
    ----------
    framework_name: str
        Framework name.
    framework_version: str
        Framework version.
    test_schema: str
        Path to the test schema markdown notebook.
    """
    if not (os.path.exists(test_schema) and os.path.isfile(test_schema)):
        m = 'Input schema file "{}" does not exist'.format(test_schema)
        logger.error(m)
        raise FileNotFoundError(m)

    schema = _load_schema(test_schema)
    _create_scaffolding(framework_name, framework_version, schema['cells'])
