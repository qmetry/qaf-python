import sys

from qaf.automation.ui.webdriver.command_tracker import CommandTracker

from qaf.automation.formatter.qaf_report.scenario.selenium_log import SeleniumLog, SeleniumLogStack
from qaf.automation.ui.webdriver.abstract_listener import DriverListener
import logging


class QAFWebDriverListener(DriverListener):
    __streaming_handler = logging.StreamHandler(sys.stdout)
    __logger = logging.getLogger()
    __logger.setLevel(logging.INFO)
    __logger.addHandler(__streaming_handler)

    def on_exception(self, driver, command_tracker: CommandTracker):
        selenium_log = SeleniumLog()
        selenium_log.commandName = command_tracker.command
        selenium_log.result = command_tracker.message
        selenium_log.args = command_tracker.parameters
        SeleniumLogStack().add_selenium_log(selenium_log)
        self.__logger.info(selenium_log.to_string())

    def after_command(self, driver, command_tracker: CommandTracker):
        if not is_command_excluded_from_logging(command_tracker.command):
            selenium_log = SeleniumLog()
            selenium_log.commandName = command_tracker.command
            selenium_log.result = 'OK' if (
                        command_tracker.response is None or 'status' not in command_tracker.response) else \
            command_tracker.response['status']
            selenium_log.args = command_tracker.parameters
            SeleniumLogStack().add_selenium_log(selenium_log)
            self.__logger.info(selenium_log.to_string())

    def before_command(self, driver, command_tracker: CommandTracker):
        self.__logger.info('Executing ' + command_tracker.command +
                           ' Parameters: ' + str(command_tracker.parameters))


excludeCommandsFromLogging = ['getHtmlSource', 'captureEntirePageScreenshotToString', 'executeScript', 'screenshot']


def is_command_excluded_from_logging(command_name: str) -> bool:
    if command_name in excludeCommandsFromLogging:
        return True
    return False
