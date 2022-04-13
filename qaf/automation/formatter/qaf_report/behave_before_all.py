from qaf.automation.formatter.qaf_report.test_results_meta_info import ReportsMetaInfo
from qaf.automation.util.datetime_util import current_timestamp
from qaf.automation.formatter.qaf_report.execution_meta_info import ExecutionMetaInfo
import os

OUTPUT_TEST_RESULTS_DIR = 'test-results'


def before_all() -> None:
    update_reports_meta_info()
    create_source_dir()
    create_execution_meta_info()


def update_reports_meta_info() -> None:
    reports_meta_info = ReportsMetaInfo(OUTPUT_TEST_RESULTS_DIR)
    reports_meta_info.name = 'Execution Reports'
    reports_meta_info.dir = os.path.join(os.getenv('REPORT_DIR'), 'json')
    reports_meta_info.startTime = current_timestamp()
    reports_meta_info.close()

    del reports_meta_info


def create_source_dir() -> None:
    if not os.path.exists(os.path.join(os.getenv('REPORT_DIR'), 'json')):
        os.makedirs(os.path.join(os.getenv('REPORT_DIR'), 'json'))
    if not os.path.exists(os.path.join(os.getenv('REPORT_DIR'), 'img')):
        os.makedirs(os.path.join(os.getenv('REPORT_DIR'), 'img'))


def create_execution_meta_info() -> None:
    ExecutionMetaInfo().startTime = current_timestamp()
    ExecutionMetaInfo().name = 'Execution Status'
