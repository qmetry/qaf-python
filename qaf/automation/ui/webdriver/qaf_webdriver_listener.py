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
import sys

from qaf.automation.core.command_log_bean import CommandLogBean
from qaf.automation.core.test_base import add_command
# from qaf.automation.formatter.qaf_report.scenario.command_log import CommandLog, CommandLogStack
from qaf.automation.ui.webdriver.abstract_listener import DriverListener
from qaf.automation.ui.webdriver.command_tracker import CommandTracker


class QAFWebDriverListener(DriverListener):
    __streaming_handler = logging.StreamHandler(sys.stdout)
    __logger = logging.getLogger()
    __logger.setLevel(logging.INFO)
    __logger.addHandler(__streaming_handler)

    def on_exception(self, driver, command_tracker: CommandTracker):
        from qaf import pluginmagager
        pluginmagager.hook.on_driver_command_failure(driver=driver, command_tracker=command_tracker)
        selenium_log = CommandLogBean()
        selenium_log.commandName = command_tracker.command
        selenium_log.result = command_tracker.message
        selenium_log.args = [str(command_tracker.parameters)]
        selenium_log.duration = int(command_tracker.end_time) - int(command_tracker.start_time)
        # CommandLogStack().add_command_log(selenium_log)
        add_command(selenium_log)
        self.__logger.info(selenium_log.to_string())

    def after_command(self, driver, command_tracker: CommandTracker):
        from qaf import pluginmagager
        pluginmagager.hook.after_driver_command(driver=driver, command_tracker=command_tracker)

        if not is_command_excluded_from_logging(command_tracker.command):
            selenium_log = CommandLogBean()
            selenium_log.commandName = command_tracker.command
            selenium_log.result = 'OK' if (
                    command_tracker.response is None or 'value' not in command_tracker.response) else \
                str(command_tracker.response['value'])
            selenium_log.args = [str(command_tracker.parameters)]
            selenium_log.duration = int(command_tracker.end_time) - int(command_tracker.start_time)
            # CommandLogStack().add_command_log(selenium_log)
            add_command(selenium_log)
            self.__logger.info(selenium_log.to_string())

    def before_command(self, driver, command_tracker: CommandTracker):
        from qaf import pluginmagager

        pluginmagager.hook.before_driver_command(driver=driver, command_tracker=command_tracker)

        self.__logger.info('Executing ' + command_tracker.command +
                           ' Parameters: ' + str(command_tracker.parameters))


excludeCommandsFromLogging = ['getHtmlSource', 'captureEntirePageScreenshotToString', 'executeScript', 'screenshot']


def is_command_excluded_from_logging(command_name: str) -> bool:
    if command_name in excludeCommandsFromLogging:
        return True
    return False
