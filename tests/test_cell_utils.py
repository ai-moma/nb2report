import pytest

from nb2report.cell_utils import *


def test_assert_is_cell():
    cell1 = {'cell_type': 'whatever', 'source': ['whatever']}
    cell2 = {'cell_type': 'whatever', 'source': ['whatever'], 'a': 2}
    cell3 = {'cell_type': 'whatever', 'source': ['whatever', 'w2']}

    assert assert_cell(cell1) is True
    assert assert_cell(cell2) is True
    assert assert_cell(cell3) is True


@pytest.mark.xfail(raises=AssertionError)
def test_not_assert_is_cell():
    cell4 = {'cell_type': 'whatever', 'source': 'whatever'}
    cell5 = {'cell_type': 2, 'source': ['whatever']}
    cell6 = {'source': ['whatever']}
    cell7 = {'cell_type': 'whatever'}

    assert assert_cell(cell4) is False
    assert assert_cell(cell5) is False
    assert assert_cell(cell6) is False
    assert assert_cell(cell7) is False


def test_is_assert():
    cell1 = {'cell_type': 'whatever', 'source': '# asserts'}
    cell2 = {'cell_type': 'whatever', 'source': '# AssertS'}
    cell3 = {'cell_type': 'whatever', 'source': '--_-# assertsaaaA'}
    cell4 = {'cell_type': 'whatever', 'source': '--_-# AsSErtsaaaA'}
    cell5 = {'cell_type': 'whatever', 'source': '# '}
    cell6 = {'cell_type': 'whatever', 'source': ''}
    cell7 = {'cell_type': 'whatever', 'source': 'gsfdgsa'}

    assert is_assert(cell1) is True
    assert is_assert(cell2) is True
    assert is_assert(cell3) is True
    assert is_assert(cell4) is True
    assert is_assert(cell5) is False
    assert is_assert(cell6) is False
    assert is_assert(cell7) is False


def test_is_list():
    assert is_list({
        'cell_type': 'markdown',
        'source': ["*"]
    }) is True

    assert is_list({
        'cell_type': 'markdown',
        'source': ["0"]
    }) is False

    assert is_list({
        'cell_type': 'markdown',
        'source': [""]
    }) is False


def test_is_title():
    assert is_title({
        'cell_type': 'markdown',
        'source': ["#"]
    }) is True

    assert is_title({
        'cell_type': 'markdown',
        'source': ["_"]
    }) is False

    assert is_title({
        'cell_type': 'markdown',
        'source': [""]
    }) is False


def test_is_markdown():
    cell1 = {'cell_type': 'markdown', 'source': ['whatever']}
    cell2 = {'cell_type': 'marKdown', 'source': ['whatever']}
    cell3 = {'cell_type': '', 'source': ['whatever']}

    assert is_markdown(cell1) is True
    assert is_markdown(cell2) is False
    assert is_markdown(cell3) is False


def test_is_code():
    cell1 = {'cell_type': 'code', 'source': ['whatever']}
    cell2 = {'cell_type': 'coDe', 'source': ['whatever']}
    cell3 = {'cell_type': '', 'source': ['whatever']}

    assert is_code(cell1) is True
    assert is_code(cell2) is False
    assert is_code(cell3) is False


def test_get_first_line():
    cell = {'cell_type': 'code', 'source': ['whatever', 'no']}

    assert get_first_line(cell) == 'whatever'


def test_get_output():
    cell1 = {
        'cell_type': 'code',
        'execution_count': 3,
        'metadata': {},
        'outputs': [
            {'data': {'text/plain': 'True'},
            'execution_count': 3,
            'metadata': {},
            'output_type': 'execute_result'}
            ],
        'source': ['True == True']
        }

    cell2 = {
        'cell_type': 'code',
        'execution_count': 3,
        'metadata': {},
        'outputs': [],
        'source': ['True == True']
        }

    assert get_output(cell1) == 'True'
    assert get_output(cell2) == 'False'
