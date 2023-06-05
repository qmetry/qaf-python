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
import re
from urllib import parse

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver.options import GenericOptions

"""
@author: Chirag Jayswal
"""


def create_driver(driver_name):
    if 'appium' in driver_name:
        return __start_appium_webdriver(driver_name)
    elif 'remote' in driver_name:
        return __start_webdriver(driver_name, is_remote_driver=True)
    else:
        return __start_webdriver(driver_name)


def __start_appium_webdriver(driver_name) -> None:
    from appium import webdriver
    from qaf.automation.ui.webdriver import qaf_web_driver as qafwebdriver

    driver_name = re.sub(r'(?i)remote|driver', '', driver_name)
    desired_capabilities = get_desired_capabilities(driver_name=driver_name)
    CM.get_bundle().set_property("driver.desiredCapabilities", desired_capabilities)
    options = GenericOptions()
    options.load_capabilities(desired_capabilities)
    __under_laying_driver = webdriver.Remote(command_executor=get_server_url(),
                                             options=options)
    CM.get_bundle().set_property("driverCapabilities", __under_laying_driver.capabilities)
    return qafwebdriver.QAFWebDriver(__under_laying_driver)


def __start_webdriver(driver_name, is_remote_driver=False) -> None:
    from qaf.automation.ui.webdriver import qaf_web_driver as qafwebdriver

    driver_name = re.sub(r'(?i)remote|driver', '', driver_name)
    desired_capabilities = get_desired_capabilities(driver_name=driver_name)
    CM.get_bundle().set_property("driver.desiredCapabilities", desired_capabilities)

    driver_options = get_driver_options(driver_name=driver_name)
    options = GenericOptions(driver_options)
    options.load_capabilities(desired_capabilities)

    if is_remote_driver:
        # Selenium Remote Driver
        class_name = 'selenium.webdriver.remote.webdriver.WebDriver'
        __under_laying_driver = load_class(class_name)(command_executor=get_server_url(),
                                                       options=options)
    else:
        if CM().contains_key(AP.DRIVER_CLASS):
            # Appium Driver
            class_name = str(CM().get_str_for_key(AP.DRIVER_CLASS))
            __under_laying_driver = load_class(class_name)(command_executor=get_server_url(),
                                                           options=options)
        else:
            service = __web_driver_manager(driver_name=driver_name)

            # Selenium Local Driver
            class_name = 'selenium.webdriver.{driver_name}.webdriver.WebDriver'.format(driver_name=driver_name)
            __under_laying_driver = load_class(class_name)(service=service, options=options)
    CM.get_bundle().set_property("driverCapabilities", __under_laying_driver.capabilities)
    return qafwebdriver.QAFWebDriver(__under_laying_driver)


def get_desired_capabilities(driver_name: str) -> dict:
    from selenium.webdriver import DesiredCapabilities

    browser_name = str(driver_name).upper()
    if browser_name in DesiredCapabilities.__dict__:
        capabilities = DesiredCapabilities.__dict__[browser_name].copy()
    else:
        capabilities = dict()
        for k in list(DesiredCapabilities.__dict__.keys()):
            if browser_name.find(k) >= 0:
                capabilities = DesiredCapabilities.__dict__[k].copy()
                break

    key = AP.DRIVER_CAPABILITY_PREFIX
    additional_capabilities = CM().get_dict_for_key(key)
    capabilities.update(additional_capabilities)

    key = AP.DRIVER_ADDITIONAL_CAPABILITIES
    additional_capabilities = CM().get_dict_for_key(key)
    capabilities.update(additional_capabilities)

    key = AP.DRIVER_ADDITIONAL_CAPABILITIES_FORMAT.format(driver_name)
    additional_capabilities = CM().get_dict_for_key(key)
    capabilities.update(additional_capabilities)

    key = AP.DRIVER_CAPABILITY_PREFIX_FORMAT.format(driver_name)
    additional_capabilities = CM().get_dict_for_key(key)
    capabilities.update(additional_capabilities)

    return capabilities


def get_driver_options(driver_name: str):
    try:
        class_name = 'selenium.webdriver.{driver_name}.options.Options'. \
            format(driver_name=driver_name)
        options = load_class(class_name)()
        return options
    except Exception as e:
        return GenericOptions()


def get_server_url() -> str:
    remote_server = str(CM().get_str_for_key(AP.REMOTE_SERVER))
    if CM().get_int_for_key(AP.REMOTE_PORT) is None:
        return remote_server

    remote_port = int(CM().get_int_for_key(AP.REMOTE_PORT))
    parsed_url = parse.urlparse(remote_server)
    if parsed_url.hostname:
        scheme = parsed_url.scheme
        remote_server = parsed_url.hostname
    else:
        scheme = "http"

    path = "/wd/hub"
    return '{scheme}://{hostname}:{port}{path}'.format(
        scheme=scheme,
        hostname=remote_server,
        port=remote_port,
        path=path
    )


def __web_driver_manager(driver_name):
    driver_name = driver_name.replace('driver', '').replace('remote', '').lower()
    driver_name_caps = str(driver_name.replace('firefox', 'gecko')).capitalize()
    class_name = 'webdriver_manager.{driver_name}.{driver_name_caps}DriverManager'.format(driver_name=driver_name,
                                                                                          driver_name_caps=driver_name_caps)
    driver_path = load_class(class_name)().install()
    driver_path = driver_path.rsplit('/', 1)[0]
    os.environ["PATH"] += os.pathsep + driver_path
    # load_class(class_name)
    return load_class('selenium.webdriver.{driver_name}.service.Service'.format(driver_name=driver_name))(driver_path)

