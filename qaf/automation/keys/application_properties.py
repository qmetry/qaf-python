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

class ApplicationProperties:
    # Reporting
    REPORT_DIR = "test.results.dir"
    JSON_REPORT_ROOT_DIR = "json.report.root.dir"
    JSON_REPORT_DIR = "json.report.dir"
    SCREENSHOT_DIR = "selenium.screenshots.dir"
    SCREENSHOT_RELATIVE_PATH = "selenium.screenshots.relative.path"
    SUCEESS_SCREENSHOT = "selenium.success.screenshots"
    FAILURE_SCREENSHOT = "selenium.failure.screenshots"
    CURRENT_TEST_NAME = "current.testcase.name"
    CURRENT_TEST_DESCRIPTION = "current.testcase.desc"
    CURRENT_TEST_RESULT = "current.testcase.result"

    # selenium
    SELENIUM_WAIT_TIMEOUT = "selenium.wait.timeout"
    REMOTE_SERVER = "remote.server"
    REMOTE_PORT = "remote.port"

    DRIVER_NAME = "driver.name"
    DRIVER_CLASS = "driver.class"

    DRIVER_CAPABILITY_PREFIX = "driver.capabilities"
    DRIVER_ADDITIONAL_CAPABILITIES = "driver.additional.capabilities"
    DRIVER_ADDITIONAL_CAPABILITIES_FORMAT = "{0}.additional.capabilities"
    DRIVER_CAPABILITY_PREFIX_FORMAT = "{0}.capabilities"

    SELENIUM_BASE_URL = "env.baseurl"
    RESOURCES = "env.resources"

    # listeners
    WEBDRIVER_COMMAND_LISTENERS = "wd.command.listeners"
    WEBELEMENT_COMMAND_LISTENERS = "we.command.listeners"
    WEBSERVICE_COMMAND_LISTENERS = "ws.command.listeners"

    ENV_DEFAULT_LANGUAGE = "env.default.locale"
    EXECUTABLE_PATH = 'executable.path'
    TESTING_APPROACH = 'testing.approach'

    SELENIUM_SINGLETON = 'selenium.singleton'
