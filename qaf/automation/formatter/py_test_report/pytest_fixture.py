#  Copyright (c) 2022 Infostretch Corporation
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

import re

import six

from qaf.automation.core.singleton import Singleton
from qaf.automation.core.test_base import tear_down, start_step, end_step, get_checkpoint_results, get_command_logs, \
    is_verification_failed, clear_assertions_log
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus
from qaf.automation.formatter.qaf_report.util.utils import step_status
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.util.datetime_util import current_timestamp

OUTPUT_TEST_RESULTS_DIR = 'test-results'


class PyTestFixture(metaclass=Singleton):
    def __init__(self):
        self.current_class = None
        self.current_test = None
        self.current_step = None
        self.obj_test_meta_info = None

    def before_session(self) -> None:
        #ProjectEnvironment.set_up()
        #
        # root_directory = os.path.join(OUTPUT_TEST_RESULTS_DIR, date_time())
        # create_directory(root_directory)
        # os.environ['REPORT_DIR'] = root_directory

        #before_all()
        pass

    def after_session(self) -> None:
        # ExecutionMetaInfo().endTime = current_timestamp()
        tear_down()

    def before_class(self, clas) -> None:
        # current_class_directory = os.path.join(os.getenv('REPORT_DIR'), 'json', re.sub('[^A-Za-z0-9]+', ' - ',
        #                                                                                re.sub('.py', '',
        #                                                                                       clas.filename)))
        # create_directory(current_class_directory)
        # os.environ['CURRENT_FEATURE_DIR'] = current_class_directory

        # ExecutionMetaInfo().add_test(re.sub('[^A-Za-z0-9]+', ' - ', re.sub('.py', '', clas.filename)))
        #
        # FeatureOverView().startTime = current_timestamp()
        # FeatureOverView().add_class(clas.name)
        pass

    def after_class(self, clas) -> None:
        # FeatureOverView().endTime = current_timestamp()
        pass

    def before_function(self, test) -> None:
        self.current_test = test
        # current_test_directory = os.path.join(os.getenv('CURRENT_FEATURE_DIR'), test.clas.name)
        # create_directory(current_test_directory)
        # os.environ['CURRENT_SCENARIO_DIR'] = current_test_directory

        # self.obj_test_meta_info = ScenarioMetaInfo()
        # self.obj_test_meta_info.startTime = current_timestamp()
        self.startTime = current_timestamp()
        clear_assertions_log()

    def after_function(self, test) -> None:
        status_name = test.status.name

        testcase_run_result = TestCaseRunResult()
        testcase_run_result.className = test.clas.name
        testcase_run_result.checkPoints = get_checkpoint_results()
        testcase_run_result.commandLogs = get_command_logs()
        testcase_run_result.starttime = self.startTime
        testcase_run_result.endtime = current_timestamp()  # self.startTime + (test.duration * 1000)
        testcase_run_result.metaData = {
            "name": test.name,
            "resultFileName": test.name,
            "referece": six.text_type(test.location),
            "groups": test.effective_tags
        }
        if test.description:
            testcase_run_result.metaData["description"] = test.description
        if test.status == PyTestStatus.failed:
            testcase_run_result.throwable = test.exception
        elif is_verification_failed():
            status_name = 'failed'
        testcase_run_result.status = status_name

        update_result(testcase_run_result)

        # ExecutionMetaInfo().update_status(status_name)
        # FeatureOverView().update_status(status_name)
        #
        # self.obj_test_meta_info.duration = test.duration * 1000
        # self.obj_test_meta_info.result = status_name
        #
        # obj_meta_data = MetaData()
        # obj_meta_data.name = test.name
        # obj_meta_data.resultFileName = test.name
        # if test.description:
        #     obj_meta_data.description = test.description
        # obj_meta_data.referece = six.text_type(test.location)
        # obj_meta_data.groups = test.effective_tags
        #
        # self.obj_test_meta_info.metaData = obj_meta_data.to_json_dict()
        # self.obj_test_meta_info.close()
        #
        # del self.obj_test_meta_info
        # self.obj_test_meta_info = None
        # Scenario(file_name=test.name).seleniumLog = CommandLogStack().get_all_command_log()

    def before_step(self, step, *args) -> None:
        self.current_step = step
        start_step(step.keyword + ' ' + step.name, [*args, ])

    def after_step(self, step) -> None:
        status = step_status(step)
        b_status = bool(re.search('(?i)pass', status)) if bool(re.search('(?i)fail|pass', status)) else None
        end_step(b_status)
