import pytest

from qaf.automation.core.qaf_exceptions import ValidationError
from qaf.automation.core.test_base import is_verification_failed, get_verification_errors, get_bundle
from qaf.automation.formatter.py_test_report.meta_info.pytest_component import *
from qaf.automation.keys.application_properties import ApplicationProperties

get_bundle().set_property(ApplicationProperties.TESTING_APPROACH,"pytest")
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    PyTestStep.status = report.outcome
    setattr(item, "rep_" + report.when, report)
    if report.when == "call":
        if not report.failed != "failed" and is_verification_failed():
            report.outcome = "failed"
            report.exception = ValidationError(str(get_verification_errors()) + " verification failed")

@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    pass


@pytest.fixture(scope="class", autouse=True)
def class_fixture(request):
    PyTestClass._before_class(request)
    yield
    PyTestClass._after_class(request)


@pytest.fixture(autouse=True)
def test_fixture(request):
    PyTestFunction._before_function(request)
    yield
    PyTestFunction._after_function(request)
