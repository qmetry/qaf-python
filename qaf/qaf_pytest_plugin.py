import json

import pytest
import six

from qaf.automation.core.test_base import is_verification_failed, get_bundle, \
    get_checkpoint_results, get_command_logs, clear_assertions_log, tear_down, get_verification_errors
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus
from qaf.automation.integration.result_updator import update_result
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.automation.util.dataprovider_util import get_testdata

get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "pytest")
dataprovider = pytest.mark.dataprovider
metadata = pytest.mark.metaData
groups = pytest.mark.groups

def pytest_addoption(parser):
    parser.addoption(
        "--dryrun", action="store_true", default=False, help="dry run bdd scenarios"
    )

def pytest_generate_tests(metafunc):
    global_testdata = get_bundle().get_raw_value("global.testdata")
    dataprovider = json.loads(global_testdata) if global_testdata else None
    for dp in [dp for dp in metafunc.definition.own_markers if dp.name.lower() == "dataprovider"]:
        dataprovider = _get_dp(dp) #JSON_DATA_TABLE
    meta_data = _get_metadata(metafunc.definition.own_markers)
    if dataprovider is not None or "JSON_DATA_TABLE" in meta_data or "datafile" in meta_data:
        param = [fixturename for fixturename in metafunc.fixturenames if "data" in fixturename.lower()]
        if param and len(param) > 0:
            testname = metafunc.definition.name
            classname = metafunc.definition.cls.__name__ if metafunc.definition.cls is not None else ""
            meta_data = meta_data | {"method": testname, "class": classname}
            testdata = meta_data["JSON_DATA_TABLE"] if "JSON_DATA_TABLE" in meta_data\
                else get_testdata(dataprovider or meta_data, meta_data)
            ids = [o.get("tcId", o.get("summary")) for o in testdata]
            metafunc.parametrize(argnames=param[0], argvalues=tuple(testdata), ids=tuple(ids))
        else:
            raise Exception("missing argument with name contains 'data' ")


def pytest_collection_modifyitems(session, config, items):
    print("pytest_collection_modifyitems")
    pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "pytest")
    outcome = yield
    report = outcome.get_result()
    # status = report.outcome
    if report.when == "call":
        if not report.failed and is_verification_failed():
            report.outcome = "failed"
            report.longrepr = 'AssertionError: {0} verification failed.'.format(get_verification_errors())
            # from _pytest._code import ExceptionInfo
            # report.excinfo = ExceptionInfo[ValidationError](
            #         excinfo=ValidationError(str(get_verification_errors()) + " verification failed"),
            #         striptext=str(get_verification_errors()) + " verification failed"
            #     )
    setattr(item, "rep_" + report.when, report)


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    # request.session.executor = ThreadPoolExecutor(max_workers=1)
    # request.session.result_updators = register_updaters()
    # get_bundle().set_property("__executor", request.session.executor)
    # get_bundle().set_property("__result_updators", request.session.result_updators)
    pass


@pytest.fixture(scope="class", autouse=True)
def class_fixture(request):
    pass


@pytest.fixture(autouse=True)
def test_fixture(request):
    clear_assertions_log()
    get_bundle().set_property(ApplicationProperties.CURRENT_TEST_NAME, request.node.name)
    get_bundle().set_property(ApplicationProperties.CURRENT_TEST_RESULT, request.node)

    yield
    # get_bundle().set_property("__executor", request.session.executor)
    # get_bundle().set_property("__result_updators", request.session.result_updators)
    report_result(request)
    tear_down()


def report_result(request):
    testcase_run_result = TestCaseRunResult()

    testcase_run_result.className = request.node.cls.__name__ if request.node.cls is not None else request.node.nodeid
    testcase_run_result.checkPoints = get_checkpoint_results().copy()
    testcase_run_result.commandLogs = get_command_logs().copy()
    testcase_run_result.starttime = int(request.node.rep_call.start * 1000)
    testcase_run_result.endtime = int(request.node.rep_call.stop * 1000)  # self.startTime + (test.duration * 1000)
    testcase_run_result.metaData = {"name": request.node.name, "resultFileName": request.node.name,
                                    "reference": six.text_type(request.node.nodeid),
                                    "description": request.node.originalname} | _get_metadata(request.node.own_markers)
    if hasattr(request.node, "callspec"):
        testcase_run_result.testData = [request.node.callspec.params]
    testcase_run_result.throwable = request.node.rep_call.longreprtext
    testcase_run_result.executionInfo = {
        "testName": "PyTest",
        "suiteName": request.session.name,
        "driverCapabilities": {
            "browser-desired-capabilities": get_bundle().get("driver.desiredCapabilities", {}).copy(),
            "browser-actual-capabilities": get_bundle().get("driverCapabilities", {}).copy()
        }
    }
    testcase_run_result.status = PyTestStatus.from_name(request.node.rep_call.outcome).name

    update_result(testcase_run_result)


def _get_metadata(markers):
    metadata = {"groups": []}
    for marker in markers:
        if marker.name.lower() == "dataprovider":
            metadata.update(_get_dp(marker))
        elif marker.args or marker.kwargs:
            metadata.update(marker.kwargs)
            if marker.args:
                if marker.name.lower() == "groups":
                    metadata["groups"]+=list(marker.args)
                else: metadata[marker.name]: marker.args
        else:
            metadata["groups"].append(marker.name)
    return metadata


def _get_dp(marker):
    return {"_dataFile": marker.args[0]} | marker.kwargs if marker.args else marker.kwargs


def pytest_collect_file(parent, file_path):
    if file_path.suffix == ".feature":
        from qaf.automation.bdd2.bdd2test_factory import BDD2File
        return BDD2File.from_parent(parent, path=file_path)
