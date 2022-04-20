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

import os

from appium import webdriver as appium_webdriver

from qaf.automation.core.load_class import load_class

from qaf.automation.ui.webdriver import qaf_web_driver as qafwebdriver
from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver.desired_capabilities import get_desired_capabilities, get_driver_options, \
    get_command_executor


class BaseDriver:
    __driver = None

    def start_driver(self) -> None:
        """
        Start web driver session by referring driver capabilities for AUT.

        Returns:
            None
        """
        if BaseDriver.__driver is not None:
            self.stop_driver()

        driver_name = str(CM().get_str_for_key(AP.DRIVER_NAME)).lower()
        if 'appium' in driver_name:
            self.__start_appium_webdriver(driver_name)
        elif 'remote' in driver_name:
            self.__start_remote_webdriver(driver_name)
        else:
            self.__web_driver_manager(driver_name=driver_name)
            self.__start_webdriver(driver_name)

    def __start_appium_webdriver(self, driver_name):
        driver_name = driver_name.replace('driver', '')

        desired_capabilities = get_desired_capabilities(driver_name=driver_name)

        remote_server = str(CM().get_str_for_key(AP.REMOTE_SERVER))
        remote_port = int(CM().get_int_for_key(AP.REMOTE_PORT))
        command_executor = get_command_executor(hostname=remote_server, port=remote_port)

        driver = appium_webdriver.Remote(command_executor=command_executor,
                                         desired_capabilities=desired_capabilities)
        BaseDriver.__driver = qafwebdriver.QAFAppiumWebDriver(driver)

    def __start_webdriver(self, driver_name):
        driver_name = driver_name.replace('driver', '')

        desired_capabilities = get_desired_capabilities(driver_name=driver_name)
        driver_options = get_driver_options(driver_name=driver_name)

        class_name = 'selenium.webdriver.{driver_name}.webdriver.WebDriver'. \
            format(driver_name=driver_name)

        driver = load_class(class_name)(options=driver_options,
                                        desired_capabilities=desired_capabilities)

        BaseDriver.__driver = qafwebdriver.QAFWebDriver(driver)

    def __start_remote_webdriver(self, driver_name):
        browser_name = driver_name.replace('driver', '').replace('remote', '')

        desired_capabilities = get_desired_capabilities(driver_name=browser_name)
        driver_options = get_driver_options(driver_name=browser_name)

        class_name = 'selenium.webdriver.remote.webdriver.WebDriver'
        remote_server = str(CM().get_str_for_key(AP.REMOTE_SERVER))
        remote_port = int(CM().get_int_for_key(AP.REMOTE_PORT))
        command_executor = get_command_executor(hostname=remote_server, port=remote_port)

        driver = load_class(class_name)(command_executor=command_executor,
                                        options=driver_options,
                                        desired_capabilities=desired_capabilities)
        BaseDriver.__driver = qafwebdriver.QAFWebDriver(driver)

    def __web_driver_manager(self, driver_name):
        driver_name = driver_name.replace('driver', '').replace('remote', '').lower()
        driver_name_caps = str(driver_name).capitalize()
        class_name = 'webdriver_manager.{driver_name}.{driver_name_caps}DriverManager'.format(driver_name=driver_name,
                                                                                              driver_name_caps=driver_name_caps)
        driver_path = load_class(class_name)().install()
        driver_path = driver_path.rsplit('/', 1)[0]
        os.environ["PATH"] += os.pathsep + driver_path

    def stop_driver(self) -> None:
        """
        Stop web driver session.

        Returns:
            None
        """
        if BaseDriver.__driver is not None:
            BaseDriver.__driver.quit()

    def get_driver(self):
        """
        Returns web driver object.

        Returns:
            webdriver: Returns web driver object.
        """
        if BaseDriver.__driver is None:
            self.start_driver()

        return BaseDriver.__driver

    @staticmethod
    def has_driver():
        if BaseDriver.__driver is None:
            return False
        return True
