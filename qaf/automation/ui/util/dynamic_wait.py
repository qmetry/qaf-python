import time

from typing import TypeVar, Generic

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from qaf.automation.core.configurations_manager import ConfigurationsManager
from qaf.automation.keys.application_properties import ApplicationProperties

POLL_FREQUENCY = 0.5  # How long to sleep inbetween calls to the method
IGNORED_EXCEPTIONS = (NoSuchElementException,)  # exceptions ignored during calls to the method
T = TypeVar('T')


class DynamicWait(Generic[T]):
    def __init__(self, inject: T, timeout, poll_frequency=POLL_FREQUENCY, ignored_exceptions=None):
        """Constructor, takes a generic instance and timeout in seconds.

                   :Args:
                    - inject - Instance of Generic Type (Ie, QAFWebElement, QAFWebDriver)
                    - timeout - Number of seconds before timing out
                    - poll_frequency - sleep interval between calls
                      By default, it is 0.5 second.
                    - ignored_exceptions - iterable structure of exception classes ignored during calls.
                      By default, it contains NoSuchElementException only.

                   Example:
                    from selenium.webdriver.support.ui import WebDriverWait \n
                    element = DynamicWait(driver, 10).until(lambda x: x.find_element_by_id("someId")) \n
                    is_disappeared = WebDriverWait(driver, 30, 1, (ElementNotVisibleException)).\ \n
                                until_not(lambda x: x.find_element_by_id("someId").is_displayed())
                """
        self._inject = inject
        self._timeout = ConfigurationsManager.get_bundle().get_int(ApplicationProperties.SELENIUM_WAIT_TIMEOUT, 5) \
            if timeout == 0 else timeout
        self._poll = poll_frequency
        # avoid the divide by zero
        if self._poll == 0:
            self._poll = POLL_FREQUENCY
        exceptions = list(IGNORED_EXCEPTIONS)
        if ignored_exceptions is not None:
            try:
                exceptions.extend(iter(ignored_exceptions))
            except TypeError:  # ignored_exceptions is not iterable
                exceptions.append(ignored_exceptions)
        self._ignored_exceptions = tuple(exceptions)

    def __repr__(self):
        return '<{0.__module__}.{0.__name__} (using "{1}")>'.format(
            type(self), str(self._inject))

    def until(self, method, message=''):
        """Calls the method provided with the driver as an argument until the \
        return value is not False."""
        screen = None
        stacktrace = None

        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._inject)
                if value:
                    if type(value) is bool:
                        return value
                    elif value[0]:
                        return value[0], value[1]
            except self._ignored_exceptions as exc:
                screen = getattr(exc, 'screen', None)
                stacktrace = getattr(exc, 'stacktrace', None)
            time.sleep(self._poll)
            if time.time() > end_time:
                break
        raise TimeoutException(message, screen, stacktrace)

    def until_not(self, method, message=''):
        """Calls the method provided with the driver as an argument until the \
        return value is False."""
        screen = None
        stacktrace = None

        end_time = time.time() + self._timeout
        while True:
            try:
                value = method(self._inject)
                if value:
                    if type(value) is bool:
                        if not value:
                            return not value
                    elif not value[0]:
                        return not value[0], value[1]
            except self._ignored_exceptions as exc:
                screen = getattr(exc, 'screen', None)
                stacktrace = getattr(exc, 'stacktrace', None)
            time.sleep(self._poll)
            if time.time() > end_time:
                break
        raise TimeoutException(message, screen, stacktrace)
