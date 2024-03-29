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


class WsListener(DriverListener):
    __streaming_handler = logging.StreamHandler(sys.stdout)
    __logger = logging.getLogger()
    __logger.setLevel(logging.INFO)
    __logger.addHandler(__streaming_handler)

    def before_command(self, driver, command_tracker: CommandTracker) -> None:
        self.__logger.info('Executing ' + command_tracker.command +
                           ' Parameters: ' + str(command_tracker.parameters))

    def after_command(self, driver, command_tracker: CommandTracker) -> None:
        commandlog = CommandLogBean()
        commandlog.commandName = command_tracker.command
        commandlog.result = command_tracker.response.text if command_tracker.response is not None else command_tracker.response['status_code']
        commandlog.args = [str(command_tracker.parameters)]
        commandlog.duration = command_tracker.end_time - command_tracker.start_time

        #CommandLogStack().add_command_log(commandlog)
        add_command(commandlog)
        self.__logger.info(commandlog.to_string())

    def on_exception(self, driver, command_tracker: CommandTracker) -> None:
        self.__logger.info('exception ' + command_tracker.command +
                           ' Parameters: ' + str(command_tracker.parameters))
        commandlog = CommandLogBean()
        commandlog.commandName = command_tracker.command
        commandlog.result = command_tracker.message
        commandlog.args = [str(command_tracker.parameters)]
        commandlog.duration = command_tracker.end_time - command_tracker.start_time
        # CommandLogStack().add_command_log(commandlog)
        add_command(commandlog)
        self.__logger.info(commandlog.to_string())
