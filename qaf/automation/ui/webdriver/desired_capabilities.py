from urllib import parse

from qaf.automation.core.load_class import load_class
from selenium.webdriver import DesiredCapabilities

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.keys.application_properties import ApplicationProperties as AP


# https://www.programcreek.com/python/example/100025/selenium.webdriver.ChromeOptions


def get_desired_capabilities(driver_name: str) -> dict:
    browser_name = str(driver_name).upper()
    capabilities = DesiredCapabilities.__dict__[browser_name].copy()

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


def get_command_executor(hostname: str, port: int) -> str:
    parsed_url = parse.urlparse(hostname)
    if parsed_url.hostname:
        scheme = parsed_url.scheme
        hostname = parsed_url.hostname
    else:
        scheme = "http"

    path = "/wd/hub"
    executor = '{scheme}://{hostname}:{port}{path}'.format(
        scheme=scheme,
        hostname=hostname,
        port=port,
        path=path
    )
    return executor
