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
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry as autoretry
from behave.model_core import Status

from qaf.automation.core.test_base import tear_down, start_step, end_step, get_command_logs, get_checkpoint_results, \
    is_verification_failed, clear_assertions_log, get_bundle
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.automation.report.utils import step_status
from qaf.automation.util.datetime_util import current_timestamp


class BaseEnvironment:

    def before_all(self, context):
        pass

    def after_all(self, context):
        tear_down()

    def before_feature(self, context, feature):
        for scenario in feature.scenarios:
            if "autoretry" in scenario.effective_tags:
                autoretry(scenario, max_attempts=2)

    def after_feature(self, context, feature):
        pass

    def before_scenario(self, context, scenario):
        self.current_scenario = scenario
        self.startTime = current_timestamp()
        clear_assertions_log()
        get_bundle().set_property(ApplicationProperties.CURRENT_TEST_NAME, scenario.name)

    def after_scenario(self, context, scenario):

        status_name = scenario.status.name

        testcase_run_result = TestCaseRunResult()
        testcase_run_result.className = scenario.feature.name
        testcase_run_result.commandLogs = get_command_logs().copy()
        testcase_run_result.starttime = self.startTime
        testcase_run_result.endtime = current_timestamp()  # self.startTime + (scenario.duration * 1000)
        testcase_run_result.metaData = {
            "name": scenario.name,
            "resultFileName": scenario.name,
            "referece": six.text_type(scenario.location),
            "groups": scenario.effective_tags
        }
        testcase_run_result.executionInfo = {
            "testName": "Behave Test",
            "suiteName": "Behave Suite",
            "driverCapabilities": {
                "browser-desired-capabilities":get_bundle().get("driver.desiredCapabilities", {}),
                "browser-actual-capabilities": get_bundle().get("driverCapabilities",{})
            }
        }
        if scenario.description:
            testcase_run_result.metaData["description"] = scenario.description

        if scenario.status != Status.passed:
            steps = scenario.steps
            for step in steps:
                if step.status == Status.failed:
                    error_message = step.error_message
                    error_message = error_message.splitlines()
                    testcase_run_result.throwable = error_message
                elif step.status == Status.skipped or step.status == Status.untested:
                    start_step(step.name, step.keyword + ' ' + step.name)
                    end_step(None)
        else:
            if is_verification_failed():
                status_name = 'failed'

        testcase_run_result.checkPoints = get_checkpoint_results().copy()
        testcase_run_result.status = status_name

        update_result(testcase_run_result)
        tear_down()

    def before_step(self, context, step):
        start_step(step.name, step.keyword + ' ' + step.name)

    def after_step(self, context, step):
        status = step_status(step)
        b_status = bool(re.search('(?i)pass', status)) if bool(re.search('(?i)fail|pass', status)) else None
        end_step(b_status)
