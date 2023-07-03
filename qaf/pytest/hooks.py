import time
from copy import deepcopy

import pytest
import six

from qaf.automation.core.test_base import is_verification_failed, get_bundle, \
    get_checkpoint_results, get_command_logs, clear_assertions_log, tear_down, get_verification_errors, \
    set_test_context, start_step, end_step
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.pytest.pytest_utils import PyTestStatus, get_metadata


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_post_finalizer(fixturedef, request):
    start_step(fixturedef.argname, fixturedef.func.__name__)
    outcome = yield
    end_step(not outcome.excinfo)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    start_step(fixturedef.argname, fixturedef.func.__name__)
    start = time.time()
    outcome = yield
    # result = fixturedef.cached_result if hasattr(fixturedef, 'cached_result') else None
    end_step(not outcome.excinfo)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    set_test_context(item)
    get_bundle().set_property(ApplicationProperties.CURRENT_TEST_NAME, item.name)
    get_bundle().set_property(ApplicationProperties.CURRENT_TEST_RESULT, item)
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    setattr(item, "report", report)

    if not report.failed and is_verification_failed():
        report.outcome = "failed"
        report.longrepr = 'AssertionError: {0} verification failed.'.format(get_verification_errors())

    report_result(item)
    tear_down()
    clear_assertions_log()


def report_result(node):
    report = node.rep_call if hasattr(node, "rep_call") else node.report
    testcase_run_result = TestCaseRunResult()
    # not isinstance(node, FixtureDef)
    testcase_run_result.isTest = report.when == "call"
    name = node.name if report.when == "call" else f'{report.when}-{node.name}'

    testcase_run_result.className = _get_class_name(node)
    testcase_run_result.checkPoints = get_checkpoint_results().copy()
    testcase_run_result.commandLogs = get_command_logs().copy()
    testcase_run_result.starttime = int(report.start * 1000)
    testcase_run_result.endtime = int(report.stop * 1000)
    metadata_from_markers = get_metadata(node.own_markers) if hasattr(node, "own_markers") else {}

    testcase_run_result.metaData = {"name": name, "resultFileName": name,
                                    "reference": six.text_type(node.nodeid),
                                    "description": node.originalname} | metadata_from_markers
    if hasattr(node, "callspec"):
        testcase_run_result.testData = [node.callspec.params]
    try:
        testcase_run_result.throwable = report.longreprtext
    except:
        testcase_run_result.throwable = str(report.longrepr[-1])
    testcase_run_result.executionInfo = {
        "testName": "PyTest",
        "suiteName": node.session.name,
        "driverCapabilities": {
            "browser-desired-capabilities": get_bundle().get("driver.desiredCapabilities", {}).copy(),
            "browser-actual-capabilities": get_bundle().get("driverCapabilities", {}).copy()
        }
    }
    testcase_run_result.status = PyTestStatus.from_name(report.outcome).name
    update_result(testcase_run_result)

    if report.when == "setup" and testcase_run_result.status != PyTestStatus.passed.name:
        # report test as skipped
        testcase_run_result_skip = deepcopy(testcase_run_result)
        testcase_run_result_skip.metaData.update({"name": node.name, "resultFileName": node.name})
        testcase_run_result_skip.status = PyTestStatus.skipped.name
        testcase_run_result_skip.isTest = True
        update_result(testcase_run_result_skip)


def _get_class_name(node):
    if hasattr(node, 'cls') and node.cls: return node.cls.__name__
    return node.nodeid.replace(f'::{node.name}', '')
