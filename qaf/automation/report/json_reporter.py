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

import json
import os
import platform
import sys
import time
from threading import Lock
from time import strftime

from qaf.automation.core.test_base import get_bundle
from qaf.automation.formatter.qaf_report.util.utils import scenario_status
from qaf.automation.integration.testcase_result_updator import TestCaseResultUpdator
from qaf.automation.integration.testcase_run_result import TestCaseRunResult
from qaf.automation.report.status_counter import StatusCounter
from qaf.automation.util.datetime_util import current_timestamp


class JsonReporter(TestCaseResultUpdator):
    """
    Result updator implementation for QAF Json reporting.
    @author: Chirag Jayswal
    """
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

    def __init__(self):
        os.environ["json.report.root.dir"] = self.REPORT_DIR
        self.suiteStatusCounters = [] #get_bundle().get_or_set("execution.suite_status_counters", [])
        self.testSetStatusCounters = [] #get_bundle().get_or_set("execution.test_set_status_counters", [])
        os.makedirs(self.JSON_REPORT_DIR, exist_ok=True)
        self.lock = Lock()

    def get_tool_name(self):
        return "QAF Json Reporter"

    def update_result(self, result: TestCaseRunResult) -> bool:

        suite_name = result.executionInfo.get("suiteName", "Default Suite")
        # testName = StringUtil.toTitleCaseIdentifier(suiteName) + "/" + StringUtil.toTitleCaseIdentifier((String)
        test_name = os.path.join(suite_name, result.executionInfo.get("testName", "Default TestSet"), str(os.getpid()))
        suit_report_dir = self.JSON_REPORT_DIR
        test_report_dir = os.path.join(suit_report_dir, test_name)

        suite_status_counter = self.get_status_counter(self.suiteStatusCounters,
                                                       StatusCounter(suite_name).with_file(suit_report_dir))
        test_status_counter = self.get_status_counter(self.testSetStatusCounters,
                                                      StatusCounter(test_name).with_file(test_report_dir))
        if result.isTest and not result.willRetry:
            suite_status_counter.add(result.status)
            test_status_counter.add(result.status)

        with self.lock:
            # suite meta - info
            self.updateSuiteMetaData(result, suite_status_counter, test_status_counter)
        # test overview
        self.updateTestOverView(result, test_status_counter)
        self.addMethodResult(result, test_status_counter)

        return True

    def updateSuiteMetaData(self, result: TestCaseRunResult, suite_status_counter: StatusCounter,
                            test_status_counter: StatusCounter):
        suite_report_file = os.path.join(suite_status_counter.file, "meta-info.json")
        # suite_report = {}
        if os.path.exists(suite_report_file):
            with open(suite_report_file) as f:
                suite_report = json.load(f)
                suite_status_counter.reset(suite_report)
                if result.isTest and not result.willRetry:
                    suite_status_counter.add(result.status)
                if test_status_counter.name not in suite_report["tests"]:
                    suite_report["tests"].append(test_status_counter.name)
        else:
            suite_report = {
                "name": suite_status_counter.name,
                # "dir": suiteStatusCounter.file,
                "startTime": result.starttime,
                "tests": [test_status_counter.name]
            }
            report_entry = {
                "name": suite_status_counter.name,
                "dir": suite_status_counter.file,
                "startTime": get_bundle().get_or_set("execution.start.ts", result.starttime)
            }
            report_meta_info_file = os.path.join(self.OUTPUT_TEST_RESULTS_DIR, "meta-info.json")
            meta_info = {"reports": []}
            if os.path.exists(report_meta_info_file):
                with open(report_meta_info_file) as f:
                    meta_info = json.load(f)
            meta_info.get("reports").insert(0, report_entry)
            # write to file
            self.write_to_file(report_meta_info_file, meta_info)


        suite_status = {
            "status": suite_status_counter.get_status(),
            "total": suite_status_counter.get_total(),
            "pass": suite_status_counter.get_pass(),
            "fail": suite_status_counter.get_fail(),
            "skip": suite_status_counter.get_skip(),
            "endTime": result.endtime or current_timestamp()
        }
        self.write_to_file(suite_report_file, suite_report | suite_status)

    def updateTestOverView(self, result: TestCaseRunResult, test_status_counter: StatusCounter):
        overview_file = os.path.join(test_status_counter.file, "overview.json")
        # test_overview = {}
        if os.path.exists(overview_file):
            with open(overview_file) as f:
                test_overview = json.load(f)
            if result.className not in test_overview.get("classes"):
                test_overview.get("classes").append(result.className)
        else:
            test_overview = {
                "startTime": result.starttime,
                "classes": [result.className],
                "envInfo": {
                    "isfw-build-info": {
                        "qaf-Type":"qaf-python",
                        "qaf-Revision":"SNAPSHOT"
                    },
                    "run-parameters": {},
                    "execution-env-info": {
                        "os.name": platform.platform(),
                        # "os.version": os.environ.get('USERNAME'),
                        # "os.arch": str(platform.architecture()),
                        "python.version": sys.version,
                        "user.name": os.environ.get('USER', os.environ.get('USERNAME', '')),
                        "host": platform.node()
                    },
                    "browser-desired-capabilities": {},
                    "browser-actual-capabilities": {}

                }
            }
            if "driverCapabilities" in result.executionInfo:
                test_overview.get("envInfo")["browser-desired-capabilities"] = get_bundle().get(
                    "driver.desiredCapabilities", {})
                test_overview.get("envInfo")["browser-actual-capabilities"] = get_bundle().get(
                    "driverCapabilities")

        test_status = {
            # "status": testStatusCounter.get_status(),
            "total": test_status_counter.get_total(),
            "pass": test_status_counter.get_pass(),
            "fail": test_status_counter.get_fail(),
            "skip": test_status_counter.get_skip(),
            "endTime": result.endtime or current_timestamp()
        }
        self.write_to_file(overview_file, test_overview | test_status)

    def addMethodResult(self, result: TestCaseRunResult, test_status_counter: StatusCounter):
        # scenario_file_path = os.path.join(self.path_to_write, result.get_name() + '.json')
        method_result_dir = os.path.join(test_status_counter.file,
                                         result.className or os.getenv('CURRENT_SCENARIO_DIR', ""))
        os.makedirs(name=method_result_dir, exist_ok=True)
        scenario_file_path = os.path.join(method_result_dir, result.get_name() + '.json')
        try:
            _dict = {
                "seleniumLog": result.commandLogs,
                "checkPoints": result.checkPoints,
                "errorTrace": "\n".join(result.throwable) if isinstance(result.throwable, list) else result.throwable,
            }
            self.write_to_file(scenario_file_path, _dict)

            method_info = {
                "index": 1,
                "type": "test" if result.isTest else "config",
                "args": result.testData,
                "metaData": result.metaData,
                "dependsOn": [],
                "startTime": result.starttime,
                "duration": (result.endtime or current_timestamp()) - result.starttime,
                "result": scenario_status(result.status.lower()),
                "passPer": 0.0
            }
            retry_count = result.executionInfo.get("retryCount", 0)
            if retry_count > 0:
                method_info["retryCount"] = retry_count

            class_meta_data = {'methods': []}

            class_info_file = os.path.join(method_result_dir, "meta-info.json")
            if os.path.exists(class_info_file):
                with open(class_info_file) as f:
                    class_meta_data = json.load(f)

            class_meta_data.get('methods').append(method_info)
            self.write_to_file(class_info_file, class_meta_data)
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def get_status_counter(counters, status_counter_to_match: StatusCounter) -> StatusCounter:
        status_counter_matches = [status_counter for status_counter in counters
                                  if status_counter.file == status_counter_to_match.file]
        if status_counter_matches:
            return status_counter_matches[0]
        else:
            counters.append(status_counter_to_match)
            # check create dir
            os.makedirs(name=status_counter_to_match.file, exist_ok=True)
            return status_counter_to_match


    @staticmethod
    def write_to_file(file_path, data):
        with open(file_path, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4, default=lambda __o: __o.to_json_dict() or __o.__dict__)
