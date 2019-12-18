import pytest
import os

from pathlib import Path
from nb2report import scaffolding


# Setup and environment asserts
BASE_DIR = Path(os.environ['BASE_DIR'])
TMP_DIR = Path(os.environ['TMP_DIR'])
RESOURCES_DIR = Path(os.environ['RESOURCES_DIR'])
SCHEMA_FILE = Path(os.environ['SCHEMA_FILE'])

if not BASE_DIR.exists() or not BASE_DIR.is_dir():
    raise FileNotFoundError('BASE_DIR has not been correctly initialized. '
                            'Current value: %s' % SCHEMA_FILE)

if not TMP_DIR.exists() or not TMP_DIR.is_dir():
    raise FileNotFoundError('TMP_DIR has not been correctly initialized. '
                            'Current value: %s' % TMP_DIR)

if not RESOURCES_DIR.exists() or not RESOURCES_DIR.is_dir():
    raise FileNotFoundError('RESOURCES_DIR has not been correctly initialized. '
                            'Current value: %s' % RESOURCES_DIR)

if not SCHEMA_FILE.exists() or not SCHEMA_FILE.is_file():
    raise FileNotFoundError('Schema file cannot be found at %s' % SCHEMA_FILE)
#################################


def test__load_schema():
    notebook = scaffolding._load_schema(SCHEMA_FILE)
    assert notebook is not None


def test__setup_base_dir():
    scaffolding.BASE_DIR = BASE_DIR
    framework_fake_name = 'tmp'
    framework_fake_version = 'test'

    scaffolding._setup_base_dir(framework_fake_name, framework_fake_version)

    assert BASE_DIR\
        .joinpath(framework_fake_name)\
        .joinpath(framework_fake_version)\
        .exists()


def test__walk_path_test():
    pass


def test__get_new_level():
    no_level, no_title = scaffolding._get_new_level('', 0)
    level1, title = scaffolding._get_new_level('# A', 0)
    level2, subtitle2 = scaffolding._get_new_level('## B', 0)
    level3, subtitle3 = scaffolding._get_new_level('### C', 0)
    level10, subtitle10 = scaffolding._get_new_level('########## D', 0)
    level_last, list_title = scaffolding._get_new_level('* F', 0)

    assert no_level == 0
    assert level1 == 1
    assert level2 == 2
    assert level3 == 3
    assert level10 == 10
    assert level_last == 1

    assert no_title == ''
    assert title == 'A'
    assert subtitle2 == 'B'
    assert subtitle3 == 'C'
    assert subtitle10 == 'D'
    assert list_title == 'F'


def test__generate_notebooks():
    sources = [
        '* NB1',
        '* NB2'
    ]

    empty_sources = []

    scaffolding._generate_notebooks(sources, TMP_DIR)
    scaffolding._generate_notebooks(empty_sources, TMP_DIR)  # test no error

    assert Path(TMP_DIR / "NB1.ipynb").exists()
    assert Path(TMP_DIR / "NB2.ipynb").exists()


def test__create_scaffolding():
    scaffolding.BASE_DIR = BASE_DIR
    framework_fake_name = 'tmp'
    framework_fake_version = 'test'

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Estructuras_de_datos"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Que_estructuras_de_datos_maneja"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "* csv\n",
                "* parquet\n",
                "nada",
                "[completar]"
            ]
        }
    ]

    scaffolding._create_scaffolding(framework_fake_name, framework_fake_version, cells)

    root_dir = BASE_DIR / framework_fake_name / framework_fake_version
    dir1 = root_dir.joinpath('Estructuras_de_datos')
    dir2 = dir1.joinpath("Que_estructuras_de_datos_maneja")

    file1 = dir2.joinpath("csv.ipynb")
    file2 = dir2.joinpath("parquet.ipynb")
    file3 = dir2.joinpath("nada.ipynb")

    assert dir1.exists() and dir1.is_dir()
    assert dir2.exists() and dir2.is_dir()
    assert file1.exists() and file1.is_file()
    assert file2.exists() and file2.is_file()
    assert not file3.exists()


def test__level_in():
    # assert it works the first time
    assert Path(scaffolding._level_in(TMP_DIR, "test_in")).exists()
    # assert it still works
    assert Path(scaffolding._level_in(TMP_DIR, "test_in")).exists()


def test__level_out():
    assert Path(scaffolding._level_out(BASE_DIR / 'tmp')).resolve() == BASE_DIR


def test_create():
    scaffolding.BASE_DIR = BASE_DIR
    framework_fake_name = 'tmp'
    framework_fake_version = 'test'

    scaffolding.create(framework_fake_name, framework_fake_version, SCHEMA_FILE)
    # assert raises no error

