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

from urllib import parse

from qaf.automation.core.load_class import load_class
from selenium.webdriver import DesiredCapabilities

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.keys.application_properties import ApplicationProperties as AP


def get_desired_capabilities(driver_name: str) -> dict:
    browser_name = str(driver_name).upper()
    if browser_name in DesiredCapabilities.__dict__:
        capabilities = DesiredCapabilities.__dict__[browser_name].copy()
    else:
        capabilities = dict()

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
    class_name = 'selenium.webdriver.{driver_name}.options.Options'. \
        format(driver_name=driver_name)
    options = load_class(class_name)()
    return options


def get_command_executor() -> str:
    remote_server = str(CM().get_str_for_key(AP.REMOTE_SERVER))
    remote_port = int(CM().get_int_for_key(AP.REMOTE_PORT))
    if CM().get_int_for_key(AP.REMOTE_PORT) is None:
        return remote_server

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
