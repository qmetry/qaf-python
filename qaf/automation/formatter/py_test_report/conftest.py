import pytest
from qaf.automation.formatter.py_test_report.meta_info.pytest_component import *


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    PyTestStep.status = report.outcome
    setattr(item, "rep_" + report.when, report)


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    PyTestSession._before_session(request)
    yield
    PyTestSession._after_session(request)


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
