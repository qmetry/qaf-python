import json
import os
import time
from time import strftime

import pytest

from qaf.automation.core import get_bundle
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.automation.util.dataprovider_util import get_testdata
from . import hooks
from .pytest_utils import get_metadata, get_dp

get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "pytest")
dataprovider = pytest.mark.dataprovider
metadata = pytest.mark.metaData
groups = pytest.mark.groups

OPT_DRYRUN = "--dryrun"
OPT_METADATA_FILTER = "--metadata-filter"


def pytest_report_header(config):
    get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "pytest")
    return ["Using Qmetry Automation Framework ...", "for web mobile and webservices test automation."]


def pytest_addoption(parser):
    parser.addoption(
        OPT_DRYRUN, action="store_true", default=False, help="dry run bdd scenarios"
    )
    parser.getgroup("general").addoption(
        OPT_METADATA_FILTER, action="store", default="", help="qaf metadata filter"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "metadata(group1, group2, key1=val1): tests case metadata.  see "
                                       "https://qmetry.github.io/qaf/latest/scenario-meta-data.html")
    config.addinivalue_line(
        "markers", "dataprovider(datafile:str, "
                   "filter=None, "
                   "from=None, to=None, "
                   "indices:[])"
                   ": external data provider. see https://qmetry.github.io/qaf/latest/maketest_data_driven.html"
    )
    config.pluginmanager.register(hooks, 'QAFListener')
    OUTPUT_TEST_RESULTS_DIR = get_bundle().get_or_set('test.results.dir',
                                                      os.environ.get('test.results.dir', "test-results"))
    REPORT_DIR = get_bundle().get_or_set('json.report.root.dir',
                                         os.environ.get('json.report.root.dir',
                                                        os.path.join(OUTPUT_TEST_RESULTS_DIR,
                                                                     strftime('%d-%m-%Y_%H_%M_%S',
                                                                              time.localtime()))))
    JSON_REPORT_DIR = get_bundle().get_or_set('json.report.dir',
                                              os.environ.get('json.report.dir',
                                                             os.path.join(REPORT_DIR, 'json')))
    os.environ["test.results.dir"] = OUTPUT_TEST_RESULTS_DIR
    os.environ["json.report.root.dir"] = REPORT_DIR
    os.environ["json.report.dir"] = JSON_REPORT_DIR
    os.makedirs(JSON_REPORT_DIR, exist_ok=True)
    # pytest report file
    report = f"{REPORT_DIR}/pytest-report.html"
    # adjust plugin options
    config.option.htmlpath = report
    config.option.self_contained_html = True


def pytest_generate_tests(metafunc):
    global_testdata = get_bundle().get_raw_value("global.testdata")
    dataprovider = json.loads(global_testdata) if global_testdata else None
    for dp in [dp for dp in metafunc.definition.own_markers if dp.name.lower() == "dataprovider"]:
        dataprovider = get_dp(dp)  # JSON_DATA_TABLE
    meta_data = get_metadata(metafunc.definition.own_markers)
    if dataprovider is not None or "JSON_DATA_TABLE" in meta_data or "datafile" in meta_data:
        param = [fixturename for fixturename in metafunc.fixturenames if "data" in fixturename.lower()]
        if param and len(param) > 0:
            testname = metafunc.definition.name
            classname = metafunc.definition.cls.__name__ if metafunc.definition.cls is not None else ""
            meta_data = meta_data | {"method": testname, "class": classname}
            testdata = meta_data["JSON_DATA_TABLE"] if "JSON_DATA_TABLE" in meta_data \
                else get_testdata(dataprovider or meta_data, meta_data)
            ids = [o.get("tcId", o.get("summary")) for o in testdata]
            metafunc.parametrize(argnames=param[0], argvalues=tuple(testdata), ids=tuple(ids))
        else:
            raise Exception("missing argument with name contains 'data' ")


def pytest_collect_file(parent, file_path):
    if file_path.suffix == ".feature":
        from qaf.automation.bdd2.factory import BDD2File
        return BDD2File.from_parent(parent, path=file_path)


def pytest_load_initial_conftests(early_config, parser, args):
    def determine(arg):
        if arg.startswith("-D"):
            key, val = arg[2:].split("=", 1)
            get_bundle().set_property(key, val)
            os.environ[key] = val
            return True
        return False

    args[:] = [arg for arg in args if not determine(arg)]
