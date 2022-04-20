#  Copyright (c) .2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
