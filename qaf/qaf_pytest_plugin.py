import pytest
import six

from qaf.automation.core.qaf_exceptions import ValidationError
from qaf.automation.core.test_base import is_verification_failed, get_verification_errors, get_bundle, \
    get_checkpoint_results, get_command_logs, clear_assertions_log, tear_down
from qaf.automation.formatter.py_test_report.meta_info.pytest_component import *
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.keys.application_properties import ApplicationProperties

get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "pytest")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    PyTestStep.status = report.outcome
    if report.when == "call":
        if not report.failed and is_verification_failed():
            report.outcome = "failed"
            report.exception = ValidationError(str(get_verification_errors()) + " verification failed")
    setattr(item, "rep_" + report.when, report)


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    pass


@pytest.fixture(scope="class", autouse=True)
def class_fixture(request):
    pass


@pytest.fixture(autouse=True)
def test_fixture(request):
    clear_assertions_log()
    yield
    report_result(request)
    tear_down()


def report_result(request):
    testcase_run_result = TestCaseRunResult()
    testcase_run_result.className = request.node.cls.__name__
    testcase_run_result.checkPoints = get_checkpoint_results()
    testcase_run_result.commandLogs = get_command_logs()
    testcase_run_result.starttime = int(request.node.rep_call.start * 1000)
    testcase_run_result.endtime = int(request.node.rep_call.stop * 1000)  # self.startTime + (test.duration * 1000)
    testcase_run_result.metaData = {"name": request.node.name, "resultFileName": request.node.name,
                                    "reference": six.text_type(request.node.nodeid),
                                    "groups": request.node.own_markers, "description": request.node.name}
    testcase_run_result.throwable = request.node.rep_call.longreprtext

    testcase_run_result.status = PyTestStatus.from_name(request.node.rep_call.outcome).name

    update_result(testcase_run_result)