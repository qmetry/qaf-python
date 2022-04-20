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

import os
import six
import re

from qaf.automation.core.singleton import Singleton

from qaf.automation.core.message_type import MessageType
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus
from qaf.automation.ui.webdriver.base_driver import BaseDriver

from qaf.automation.core.project_environment import ProjectEnvironment
from qaf.automation.formatter.qaf_report.behave_before_all import before_all
from qaf.automation.formatter.qaf_report.scenario.scenario_meta_info import ScenarioMetaInfo, MetaData
from qaf.automation.formatter.qaf_report.scenario.scenario import Scenario
from qaf.automation.formatter.qaf_report.feature.feature_overview import FeatureOverView
from qaf.automation.formatter.qaf_report.execution_meta_info import ExecutionMetaInfo
from qaf.automation.formatter.qaf_report.scenario.selenium_log import SeleniumLogStack
from qaf.automation.formatter.qaf_report.step.step import Step
from qaf.automation.util.datetime_util import date_time, current_timestamp
from qaf.automation.util.directory_util import create_directory

OUTPUT_TEST_RESULTS_DIR = 'test-results'


class PyTestFixture(metaclass=Singleton):
    def __init__(self):
        self.current_class = None
        self.current_test = None
        self.current_step = None
        self.obj_test_meta_info = None

    def before_session(self) -> None:
        ProjectEnvironment.set_up()

        root_directory = os.path.join(OUTPUT_TEST_RESULTS_DIR, date_time())
        create_directory(root_directory)
        os.environ['REPORT_DIR'] = root_directory

        before_all()

    def after_session(self) -> None:
        ExecutionMetaInfo().endTime = current_timestamp()
        BaseDriver().stop_driver()

    def before_class(self, clas) -> None:
        current_class_directory = os.path.join(os.getenv('REPORT_DIR'), 'json', re.sub('[^A-Za-z0-9]+', ' - ',
                                                                                       re.sub('.py', '',
                                                                                              clas.filename)))
        create_directory(current_class_directory)
        os.environ['CURRENT_FEATURE_DIR'] = current_class_directory

        ExecutionMetaInfo().add_test(re.sub('[^A-Za-z0-9]+', ' - ', re.sub('.py', '', clas.filename)))

        FeatureOverView().startTime = current_timestamp()
        FeatureOverView().add_class(clas.name)

    def after_class(self, clas) -> None:
        FeatureOverView().endTime = current_timestamp()

    def before_function(self, test) -> None:
        self.current_test = test
        current_test_directory = os.path.join(os.getenv('CURRENT_FEATURE_DIR'), test.clas.name)
        create_directory(current_test_directory)
        os.environ['CURRENT_SCENARIO_DIR'] = current_test_directory

        self.obj_test_meta_info = ScenarioMetaInfo()
        self.obj_test_meta_info.startTime = current_timestamp()

    def after_function(self, test) -> None:
        status_name = test.status.name

        if test.status == PyTestStatus.failed:
            Scenario(file_name=test.name).errorTrace = test.exception
        else:
            checkPoints = Scenario(file_name=self.current_test.name).checkPoints
            for checkPoint in checkPoints:
                if checkPoint['type'] == MessageType.TestStepFail:
                    status_name = 'failed'
                    break

        ExecutionMetaInfo().update_status(status_name)
        FeatureOverView().update_status(status_name)

        self.obj_test_meta_info.duration = test.duration * 1000
        self.obj_test_meta_info.result = status_name

        obj_meta_data = MetaData()
        obj_meta_data.name = test.name
        obj_meta_data.resultFileName = test.name
        if test.description:
            obj_meta_data.description = test.description
        obj_meta_data.referece = six.text_type(test.location)
        obj_meta_data.groups = test.effective_tags

        self.obj_test_meta_info.metaData = obj_meta_data.to_json_dict()
        self.obj_test_meta_info.close()

        del self.obj_test_meta_info
        self.obj_test_meta_info = None
        Scenario(file_name=test.name).seleniumLog = SeleniumLogStack().get_all_selenium_log()

    def before_step(self, step) -> None:
        self.current_step = step

    def after_step(self, step) -> None:
        obj_step = Step()
        obj_step.start_behave_step(step)
        obj_step.stop_behave_step(step)
        Scenario(file_name=self.current_test.name).add_checkPoints(obj_step.obj_check_point)
        del obj_step
