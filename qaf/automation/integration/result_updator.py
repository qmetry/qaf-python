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
import logging
from concurrent.futures import ThreadPoolExecutor

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.report.json_reporter import JsonReporter


def register_updaters():
    listeners = [JsonReporter()]
    logging.getLogger().info("Registered " + listeners[0].get_tool_name())

    if CM().contains_key(AP.RESULT_UPDATERS):
        try:
            class_name = CM().get_str_for_key(AP.RESULT_UPDATERS)
            result_updater = load_class(class_name)()
            listeners.append(result_updater)
            logging.getLogger().info("Registered " + result_updater.get_tool_name())
        except Exception as e:
            logging.getLogger().exception("Unable to Registered " + class_name)
    return listeners


# result_updaters = register_updaters()
def submit_result(result, result_updater):
    try:
        logging.getLogger().info(
            result_updater.get_tool_name() + " updating::" + result.get_name() + " - " + result.status)
        executor = CM.get_bundle().get_or_set("__executor", ThreadPoolExecutor(max_workers=1))
        executor.submit(result_updater.update_result,result)
    except Exception:
        logging.getLogger().exception(
            result_updater.get_tool_name() + " Unable to update result::" + result.get_name() + " - " + result.status)


def update_result(result):
    # TODO: use executor https://docs.python.org/3/library/concurrent.futures.html
    # from multiprocessing import parent_process
    result_updaters = CM.get_bundle().get_or_set("__result_updators", register_updaters())
    if result_updaters is not None:
        for result_updater in result_updaters:
            submit_result(result, result_updater)