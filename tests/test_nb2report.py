import os
import shutil


from click.testing import CliRunner
from nb2report import nb2report

# Environment variables
SHORT_SCAFFOLDING = os.getenv('SHORT_SCAFFOLDING')
DUMMY_ASSERT_TRUE = os.getenv('DUMMY_ASSERT_TRUE')
TMP_DIR = os.getenv('TMP_DIR')

# CMD execution
SCAFFOLDING = ['-n', f'{TMP_DIR}/tmptest', '-v', '0.0.0', '-i', SHORT_SCAFFOLDING]
REPORTING = ['-n', f'{TMP_DIR}/tmptest', '-v', '.']


def test_create_scaffolding():

    runner = CliRunner()
    result = runner.invoke(nb2report.create_scaffolding, SCAFFOLDING)

    assert os.path.isdir(f'{TMP_DIR}/tmptest')
    assert result.exit_code == 0


def test_create_report():

    runner = CliRunner()
    result = runner.invoke(nb2report.create_report, REPORTING)

    assert result.exit_code == 0
    assert os.path.isfile(f'{TMP_DIR}/tmptest/{nb2report.reporting.REPORTING_FILE_NAME}')
    shutil.rmtree(f'{TMP_DIR}/tmptest')
