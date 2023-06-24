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
from behave.model_core import Status

from qaf.automation.core.test_base import tear_down, start_step, end_step, get_command_logs, get_checkpoint_results, \
    is_verification_failed, clear_assertions_log, get_bundle, get_verification_errors, set_test_context
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.automation.report.utils import step_status
from qaf.automation.util.datetime_util import current_timestamp

user_hooks = {
    "before_scenario": [],
    "after_scenario": [],
    "before_step": [],
    "after_step": []
}


def add_before_scenario_hook(fun):
    user_hooks["before_scenario"].append(fun)


def before_scenario(context, scenario):
    set_test_context(context)
    get_bundle().set_property(ApplicationProperties.CURRENT_TEST_NAME, scenario.name)
    for user_hook in user_hooks['before_scenario']:
        user_hook(context, scenario)
    clear_assertions_log()
    context.startTime = current_timestamp()


def after_scenario(context, scenario):
    for user_hook in user_hooks['after_scenario']:
        user_hook(context, scenario)

    status_name = scenario.status.name

    testcase_run_result = TestCaseRunResult()
    testcase_run_result.className = scenario.feature.name
    testcase_run_result.commandLogs = get_command_logs().copy()
    testcase_run_result.endtime = current_timestamp()  # self.startTime + (scenario.duration * 1000)
    testcase_run_result.starttime = context.startTime  # testcase_run_result.endtime - (scenario.duration * 1000)

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
            "browser-desired-capabilities": get_bundle().get("driver.desiredCapabilities", {}),
            "browser-actual-capabilities": get_bundle().get("driverCapabilities", {})
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
            elif step.status in (Status.skipped, Status.untested, Status.undefined):
                b_success = None
                suffix = ''
                if step.status is Status.undefined:
                    suffix = "::Not Found"
                    b_success = False
                start_step(step.name, f'{step.keyword} {step.name} {suffix}')
                end_step(b_success, step.status.name)
    else:
        if is_verification_failed():
            scenario.status = Status.failed
            status_name = 'failed'
            scenario.error_message = 'AssertionError: {0} verification failed.'.format(get_verification_errors())
            testcase_run_result.throwable = scenario.error_message

    testcase_run_result.checkPoints = get_checkpoint_results().copy()
    testcase_run_result.status = status_name

    update_result(testcase_run_result)
    tear_down()


def before_step(context, step):
    for user_hook in user_hooks['before_step']:
        user_hook(context, step)
    start_step(step.name, step.keyword + ' ' + step.name)


def after_step(context, step):
    for user_hook in user_hooks['after_step']:
        user_hook(context, step)
    status = step_status(step)
    b_status = bool(re.search('(?i)pass', status)) if bool(re.search('(?i)fail|pass', status)) else None
    end_step(b_status)
