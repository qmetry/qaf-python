#  Copyright (c) .2022 Infostretch Corporation
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

from typing import Optional

from selenium.webdriver.support.wait import WebDriverWait

from qaf.automation.ui import js_toolkit
from qaf.automation.ui.util.qaf_wd_expected_conditions import WaitForAjax
from qaf.automation.ui.webdriver.qaf_find_by import get_find_by
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from appium.webdriver.webdriver import WebDriver as AppiumRemoteWebDriver

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver.command_tracker import CommandTracker
from qaf.automation.ui.webdriver import qaf_web_element as qafwebelement, base_driver
from qaf.automation.ui.webdriver.qaf_webdriver_listener import QAFWebDriverListener


class QAFWebDriver(RemoteWebDriver):

    def __init__(self, driver, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, options=None):
        self.__driver = driver
        self.w3c = False

        self.__listeners = []
        self.__listeners.append(QAFWebDriverListener())

        RemoteWebDriver.__init__(self, command_executor=driver.command_executor,
                                 desired_capabilities=driver.desired_capabilities,
                                 browser_profile=browser_profile,
                                 proxy=proxy,
                                 keep_alive=keep_alive, file_detector=file_detector, options=options)

        if CM().contains_key(AP.WEBDRIVER_COMMAND_LISTENERS):
            class_name = CM().get_str_for_key(AP.WEBDRIVER_COMMAND_LISTENERS)
            self.__listeners.append(load_class(class_name)())

    def start_session(self, capabilities: dict, browser_profile=None) -> None:
        self.command_executor = self.__driver.command_executor
        self.capabilities = self.__driver.capabilities
        if hasattr(self.command_executor, 'w3c') and self.command_executor.w3c:
            self.w3c = self.command_executor.w3c is None
        self.session_id = self.__driver.session_id

    def find_element(self, by=By.ID, value=None, key=None) -> qafwebelement.QAFWebElement:
        if key is not None and len(key) > 0:
            value = CM().get_str_for_key(key, default_value=key)
            by, value = get_find_by(value)

        web_element = super(QAFWebDriver, self).find_element(by=by, value=value)
        qaf_web_element = qafwebelement.QAFWebElement.create_instance_using_webelement(web_element)
        qaf_web_element._parent = self
        qaf_web_element.by = by
        qaf_web_element.locator = value
        qaf_web_element.description = value
        return qaf_web_element

    def find_elements(self, by: Optional[str] = By.ID, value: Optional[str] = None, key: Optional[str] = None) -> [
        qafwebelement.QAFWebElement]:
        if key is not None and len(key) > 0:
            value = CM().get_str_for_key(key, default_value=key)
            by, value = get_find_by(value)

        web_elements = super(QAFWebDriver, self).find_elements(by=by, value=value)
        qaf_web_elements = []
        for web_element in web_elements:
            qaf_web_element = qafwebelement.QAFWebElement.create_instance_using_webelement(web_element)
            qaf_web_element._parent = self
            qaf_web_element.by = by
            qaf_web_element.locator = value
            qaf_web_element.description = value
            qaf_web_elements.append(qaf_web_element)
        return qaf_web_elements

    def wait_for_ajax(self, jstoolkit: Optional[str] = js_toolkit.GLOBAL_WAIT_CONDITION, wait_time: Optional[int] = 0):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = 'Wait time out for ajax to complete'
        return WebDriverWait(base_driver.BaseDriver().get_driver(), wait_time_out).until(
            WaitForAjax(jstoolkit), message
        )

    def execute(self, driver_command: str, params: dict = None) -> dict:
        command_tracker = CommandTracker(driver_command, params)
        self.before_command(command_tracker)

        try:
            if command_tracker.response is None:
                response = super(QAFWebDriver, self).execute(command_tracker.command,
                                                             command_tracker.parameters)
                command_tracker.response = response
        except Exception as e:
            self.on_exception(command_tracker)
            command_tracker.exception = e

        if command_tracker.has_exception():
            if command_tracker.retry:
                response = super(QAFWebDriver, self).execute(command_tracker.command,
                                                             command_tracker.parameters)
                command_tracker.response = response
                command_tracker.exception = None
            else:
                raise command_tracker.exception

        self.after_command(command_tracker)
        return command_tracker.response

    # Listener methods
    def before_command(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.before_command(self, command_tracker)

    def after_command(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.after_command(self, command_tracker)

    def on_exception(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.on_exception(self, command_tracker)


class QAFAppiumWebDriver(AppiumRemoteWebDriver, QAFWebDriver):
    pass
