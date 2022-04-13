from qaf.automation.ui.webdriver.base_driver import BaseDriver
from qaf.automation.ui.webdriver.qaf_web_driver import QAFWebDriver


class BaseTestPage:
    @property
    def driver(self):
        return QAFWebDriver(BaseDriver().get_driver())
