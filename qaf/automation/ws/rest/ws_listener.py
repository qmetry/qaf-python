import logging
import sys

from qaf.automation.ui.webdriver.command_tracker import CommandTracker

from qaf.automation.formatter.qaf_report.scenario.selenium_log import SeleniumLog, SeleniumLogStack
from qaf.automation.ui.webdriver.abstract_listener import DriverListener


class WsListener(DriverListener):
    __streaming_handler = logging.StreamHandler(sys.stdout)
    __logger = logging.getLogger()
    __logger.setLevel(logging.INFO)
    __logger.addHandler(__streaming_handler)

    def before_command(self, driver, command_tracker: CommandTracker) -> None:
        selenium_log = SeleniumLog()
        selenium_log.commandName = command_tracker.command
        selenium_log.result = command_tracker.message
        selenium_log.args = command_tracker.parameters
        SeleniumLogStack().add_selenium_log(selenium_log)
        self.__logger.info(selenium_log.to_string())

    def after_command(self, driver, command_tracker: CommandTracker) -> None:
        selenium_log = SeleniumLog()
        selenium_log.commandName = command_tracker.command
        selenium_log.result = command_tracker.response if command_tracker.response is not None else command_tracker.response['status_code']
        selenium_log.args = command_tracker.parameters
        SeleniumLogStack().add_selenium_log(selenium_log)
        self.__logger.info(selenium_log.to_string())

    def on_exception(self, driver, command_tracker: CommandTracker) -> None:
        self.__logger.info('Executing ' + command_tracker.command +
                           ' Parameters: ' + str(command_tracker.parameters))
