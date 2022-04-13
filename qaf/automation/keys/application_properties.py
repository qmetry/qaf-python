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
