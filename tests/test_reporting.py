import pytest
import os

from pathlib import Path
from nb2report import reporting


# Setup and environment asserts
BASE_DIR = Path(os.environ['BASE_DIR'])
TMP_DIR = Path(os.environ['TMP_DIR'])
RESOURCES_DIR = Path(os.environ['RESOURCES_DIR'])
EMPTY_NOTEBOOK = Path(os.environ['EMPTY_NOTEBOOK'])
DUMMY_ASSERT_TRUE = Path(os.environ['DUMMY_ASSERT_TRUE'])
DUMMY_ASSERT_FALSE = Path(os.environ['DUMMY_ASSERT_FALSE'])

if not BASE_DIR.exists() or not BASE_DIR.is_dir():
    raise FileNotFoundError('BASE_DIR has not been correctly initialized. '
                            'Current value: %s' % BASE_DIR)

if not TMP_DIR.exists() or not TMP_DIR.is_dir():
    raise FileNotFoundError('TMP_DIR has not been correctly initialized. '
                            'Current value: %s' % TMP_DIR)

if not RESOURCES_DIR.exists() or not RESOURCES_DIR.is_dir():
    raise FileNotFoundError('RESOURCES_DIR has not been correctly initialized. '
                            'Current value: %s' % RESOURCES_DIR)

if not EMPTY_NOTEBOOK.exists() or not EMPTY_NOTEBOOK.is_file():
    raise FileNotFoundError('Schema file cannot be found at %s' % EMPTY_NOTEBOOK)
#################################


def test__explore_scaffolding():
    pass


def test__add_report():
    reporting._add_report('test1', 'OK', 'color1')
    reporting._add_report('test2', 'KO', 'color2')

    assert len(reporting.REPORTING_ITEMS) == 2

    assert reporting.REPORTING_ITEMS[0]['title'] == 'test1'
    assert reporting.REPORTING_ITEMS[0]['color'] == 'color1'
    assert reporting.REPORTING_ITEMS[0]['supported'] == 'OK'
    assert reporting.REPORTING_ITEMS[0]['supported_color'] == 'green'

    assert reporting.REPORTING_ITEMS[1]['title'] == 'test2'
    assert reporting.REPORTING_ITEMS[1]['color'] == 'color2'
    assert reporting.REPORTING_ITEMS[1]['supported'] == 'KO'
    assert reporting.REPORTING_ITEMS[1]['supported_color'] == 'red'


def test__load_notebook():
    # schema file is not an output notebook but it is a notebook
    # it should read it anyway
    assert isinstance(reporting._load_notebook(EMPTY_NOTEBOOK), dict)


def test__get_assert_cell_index():
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "outputs": [],
            "source": [
                "blablabla",
                "blablabla"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Asserts\n",
                       "\n",
                       "Note: automatic tests will check all asserts to be true"
                       ]
        }
    ]

    assert reporting._get_assert_cell_index(cells) == 1


@pytest.mark.xfail(raises=LookupError)
def test__get_assert_cell_index_empty_cell():
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "outputs": [],
            "source": ["blablabla", "blablabla"]
        }
    ]

    reporting._get_assert_cell_index(cells)


def test__clean_output():
    assert reporting._clean_output("Out[1]: True\n") == "True"
    assert reporting._clean_output("Out[1123]: hola") == "hola"
    assert reporting._clean_output("OuT[9874]:     True") == "True"
    assert reporting._clean_output("HolaQueTal[0546]:    True\n") == "True"


def test__get_interpreter():
    reporting.IPYTHON_INTERPRETER = None
    assert reporting.IPYTHON_INTERPRETER is None

    reporting._get_interpreter()
    assert reporting.IPYTHON_INTERPRETER


def test__run_cell():
    assert reporting._run_cell("print('HOLA')") == 'HOLA'
    assert reporting._run_cell("") == ''
    assert reporting._run_cell("1 < 2") == 'True'
    assert reporting._run_cell("1 > 2") == 'False'


def test__evaluate_output():
    assert reporting._evaluate_output('False') is False
    assert reporting._evaluate_output('false') is False
    assert reporting._evaluate_output('fAlse') is False
    assert reporting._evaluate_output('FALSE') is False
    assert reporting._evaluate_output('FalsE') is False
    assert reporting._evaluate_output('falSE') is False

    assert reporting._evaluate_output('True') is True
    assert reporting._evaluate_output('true') is True
    assert reporting._evaluate_output('TruE') is True
    assert reporting._evaluate_output('truE') is True
    assert reporting._evaluate_output('TrUE') is True
    assert reporting._evaluate_output('tRUe') is True


@pytest.mark.xfail(raises=Exception)
def test__evaluate_output_exception(): reporting._evaluate_output(1)


def test__evaluate_results():
    assert reporting._evaluate_results([True]) == 'OK'
    assert reporting._evaluate_results([True, True]) == 'OK'

    assert reporting._evaluate_results([False]) == 'KO'
    assert reporting._evaluate_results([]) == 'KO'
    assert reporting._evaluate_results([1, 3, 5]) == 'KO'
    assert reporting._evaluate_results([True, True, False]) == 'KO'
    assert reporting._evaluate_results([False, True, True]) == 'KO'
    assert reporting._evaluate_results([True, False, True]) == 'KO'
    assert reporting._evaluate_results([False, False, False]) == 'KO'


def test__execute_test():
    assert reporting._execute_test(DUMMY_ASSERT_TRUE) == 'OK'
    assert reporting._execute_test(DUMMY_ASSERT_FALSE) == 'KO'


def test_generate_summary():
    reporting.BASE_DIR = BASE_DIR
    framework_fake_name = 'tmp'
    framework_fake_version = '.'

    summary_path = TMP_DIR / reporting.REPORTING_FILE_NAME

    reporting.generate_summary(framework_fake_name, framework_fake_version)

    assert summary_path.exists() and summary_path.is_file()
