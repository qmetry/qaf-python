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

from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement
from selenium.webdriver.support.wait import WebDriverWait

from qaf.automation.core.message_type import MessageType
from qaf.automation.ui.webdriver import qaf_test_base
from qaf.automation.ui.webdriver.qaf_find_by import get_find_by
from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.core.reporter import Reporter
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.util.qaf_wd_expected_conditions import *
from qaf.automation.ui.webdriver.command_tracker import Stage, CommandTracker


class QAFWebElement(RemoteWebElement):
    def __init__(self, key: str, cacheable: Optional[bool] = False) -> None:

        self.locator = None
        self.by = None
        self.description = None
        self._parent_element = None
        self._listeners = []
        self.cacheable = cacheable

        if len(key) > 0:
            parent = qaf_test_base.QAFTestBase().get_driver()
            value = CM().get_str_for_key(key, default_value=key)
            self.by, self.locator = get_find_by(value, w3c=parent.w3c)
            self.description = self.locator
            self.cacheable = cacheable
            self._id = -1
            RemoteWebElement.__init__(self, parent=parent, id_=self.id, w3c=parent.w3c)

        if CM().contains_key(AP.WEBELEMENT_COMMAND_LISTENERS):
            class_name = CM().get_str_for_key(AP.WEBELEMENT_COMMAND_LISTENERS)
            self._listeners.append(load_class(class_name)())

    @classmethod
    def create_instance_using_webelement(cls, remote_webelement, cacheable: Optional[bool] = False):
        cls.locator = None
        cls.by = None
        cls.description = None
        cls._parent_element = None
        cls._listeners = []
        cls.cacheable = cacheable

        cls._id = remote_webelement.id
        cls._w3c = remote_webelement._w3c
        return cls(key='')

    def get_description(self, msg: Optional[str] = '') -> str:
        return msg if len(msg) > 0 else self.locator

    def find_element(self, by: Optional[str] = By.ID, value: Optional[str] = None):
        web_element = super(QAFWebElement, self).find_element(by=by, value=value)
        qaf_web_element = QAFWebElement.create_instance_using_webelement(web_element)
        qaf_web_element._parent_element = self
        qaf_web_element._parent = self._parent_element.parent
        qaf_web_element.by = by
        qaf_web_element.locator = value
        qaf_web_element.description = value
        return qaf_web_element

    def find_elements(self, by: Optional[str] = By.ID, value: Optional[str] = None):
        web_elements = super(QAFWebElement, self).find_elements(by=by, value=value)
        qaf_web_elements = []
        for web_element in web_elements:
            qaf_web_element = QAFWebElement.create_instance_using_webelement(web_element)
            qaf_web_element._parent_element = self
            qaf_web_element._parent = self._parent_element.parent
            qaf_web_element.by = by
            qaf_web_element.locator = value
            qaf_web_element.description = value
            qaf_web_elements.append(qaf_web_element)
        return qaf_web_elements

    def wait_for_visible(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = 'Wait time out for ' + self.description + ' to be visible'
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForVisible((self.by, self.locator)), message
        )

    def wait_for_not_visible(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotVisible((self.by, self.locator))
        )

    def wait_for_disabled(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be disabled"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForDisabled((self.by, self.locator)), message
        )

    def wait_for_enabled(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be enabled"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForEnabled((self.by, self.locator)), message
        )

    def wait_for_present(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be present"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForPresent((self.by, self.locator)), message
        )

    def wait_for_not_present(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to not be present"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotPresent((self.by, self.locator)), message
        )

    def wait_for_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " text " + text_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForText((self.by, self.locator), text_), message
        )

    def wait_for_containing_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " containing text " + text_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForContainingText((self.by, self.locator), text_), message
        )

    def wait_for_not_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " text not " + text_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotText((self.by, self.locator), text_), message
        )

    def wait_for_not_containing_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " containing text not " + text_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotContainingText((self.by, self.locator), text_), message
        )

    def wait_for_value(self, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " value " + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForValue((self.by, self.locator), value_), message
        )

    def wait_for_not_value(self, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " value not " + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotValue((self.by, self.locator), value_), message
        )

    def wait_for_selected(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " to be selected"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForSelected((self.by, self.locator)), message
        )

    def wait_for_not_selected(self, wait_time: Optional[int] = 0) -> bool:
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " not to be selected"
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotSelected((self.by, self.locator)), message
        )

    def wait_for_attribute(self, attr_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " " + attr_ + " = " + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForAttribute((self.by, self.locator), attr_, value_), message
        )

    def wait_for_not_attribute(self, attr_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " " + attr_ + " != " + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotAttribute((self.by, self.locator), attr_, value_), message
        )

    def wait_for_css_class(self, class_name_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have css class " + class_name_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForCssClass((self.by, self.locator), class_name_), message
        )

    def wait_for_not_css_class(self, class_name_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have not css class " + class_name_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotCssClass((self.by, self.locator), class_name_), message
        )

    def wait_for_css_style(self, style_name_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have css style " + style_name_ + "=" + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForCssStyle((self.by, self.locator), style_name_, value_), message
        )

    def wait_for_not_css_style(self, style_name_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        wait_time_out = CM().get_int_for_key(AP.SELENIUM_WAIT_TIMEOUT) \
            if wait_time == 0 else wait_time
        message = "Wait time out for " + self.description + " have not css style " + style_name_ + "=" + value_
        return WebDriverWait(qaf_test_base.QAFTestBase().get_driver(), wait_time_out).until(
            WaitForNotCssStyle((self.by, self.locator), style_name_, value_), message
        )

    def __ensure_present(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_present()
        except TimeoutException:
            outcome = False
            self.report("present", outcome, msg)
        return outcome

    def verify_present(self, msg: Optional[str] = '') -> bool:
        outcome = self.__ensure_present(msg)
        if outcome:
            msg = self.get_description(msg)
            self.report("present", outcome, msg)
        return outcome

    def verify_not_present(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_not_present()
        except TimeoutException:
            outcome = False
        self.report("notpresent", outcome, msg)
        return outcome

    def verify_visible(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_visible()
        except TimeoutException:
            outcome = False
        self.report("visible", outcome, msg)
        return outcome

    def verify_not_visible(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_not_visible()
        except TimeoutException:
            outcome = False
        self.report("notvisible", outcome, msg)
        return outcome

    def verify_enabled(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_enabled()
        except TimeoutException:
            outcome = False
        self.report("enabled", outcome, msg)
        return outcome

    def verify_disabled(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_disabled()
        except TimeoutException:
            outcome = False
        self.report("disabled", outcome, msg)
        return outcome

    def verify_text(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("text", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_text_contain(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_containing_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("text", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_not_text(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("nottext", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_not_text_contains(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_containing_text(text_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("nottext", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_value(self, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_value(value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("value", outcome, msg, expected=value_, actual=actaul_)
        return outcome

    def verify_not_value(self, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_value(value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notvalue", outcome, msg, expected=value_, actual=actaul_)
        return outcome

    def verify_selected(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.wait_for_selected()
        except TimeoutException:
            outcome = False
        self.report("selected", outcome, msg)
        return outcome

    def verify_not_selected(self, msg: Optional[str] = '') -> bool:
        outcome = True
        msg = self.get_description(msg)
        try:
            self.verify_not_selected()
        except TimeoutException:
            outcome = False
        self.report("notselected", outcome, msg)
        return outcome

    def verify_attribute(self, attr_: str, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_attribute(attr_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("attribute", outcome, msg, op=attr_, expected=value_, actual=actaul_)
        return outcome

    def verify_not_attribute(self, attr_: str, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_attribute(attr_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notattribute", outcome, msg, op=attr_, expected=value_, actual=actaul_)
        return outcome

    def verify_css_class(self, class_name_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_css_class(class_name_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("cssclass", outcome, msg, expected=class_name_, actual=actaul_)
        return outcome

    def verify_not_css_class(self, class_name_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_css_class(class_name_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notcssclass", outcome, msg, expected=class_name_, actual=actaul_)
        return outcome

    def verify_css_style(self, style_name_: str, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_css_style(style_name_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("cssstyle", outcome, msg, op=style_name_, expected=value_, actual=actaul_)
        return outcome

    def verify_not_css_style(self, style_name_: str, value_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_css_style(style_name_, value_)
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            outcome = False
        self.report("notcssstyle", outcome, msg, op=style_name_, expected=value_, actual=actaul_)
        return outcome

    def assert_present(self, msg: Optional[str] = '') -> None:
        if not self.verify_present(msg):
            raise AssertionError

    def assert_not_present(self, msg: Optional[str] = '') -> None:
        if not self.verify_not_present(msg):
            raise AssertionError

    def assert_visible(self, msg: Optional[str] = '') -> None:
        if not self.verify_visible(msg):
            raise AssertionError

    def assert_not_visible(self, msg: Optional[str] = '') -> None:
        if not self.verify_not_visible(msg):
            raise AssertionError

    def assert_enabled(self, msg: Optional[str] = '') -> None:
        if not self.verify_enabled(msg):
            raise AssertionError

    def assert_disabled(self, msg: Optional[str] = '') -> None:
        if not self.verify_disabled(msg):
            raise AssertionError

    def assert_text(self, text_, msg: Optional[str] = '') -> None:
        if not self.verify_text(text_, msg):
            raise AssertionError

    def assert_text_contain(self, text_, msg: Optional[str] = '') -> None:
        if not self.verify_text_contain(text_, msg):
            raise AssertionError

    def assert_not_text(self, text_, msg: Optional[str] = '') -> None:
        if not self.verify_not_text(text_, msg):
            raise AssertionError

    def assert_not_text_contains(self, text_, msg: Optional[str] = '') -> None:
        if not self.verify_not_text_contains(text_, msg):
            raise AssertionError

    def assert_value(self, value_, msg: Optional[str] = '') -> None:
        if not self.verify_value(value_, msg):
            raise AssertionError

    def assert_not_value(self, value_, msg: Optional[str] = '') -> None:
        if not self.verify_not_value(value_, msg):
            raise AssertionError

    def assert_selected(self, msg: Optional[str] = '') -> None:
        if not self.verify_selected(msg):
            raise AssertionError

    def assert_not_selected(self, msg: Optional[str] = '') -> None:
        if not self.verify_not_selected(msg):
            raise AssertionError

    def assert_attribute(self, attr_, value_, msg: Optional[str] = '') -> None:
        if not self.verify_attribute(attr_, value_, msg):
            raise AssertionError

    def assert_not_attribute(self, attr_, value_, msg: Optional[str] = '') -> None:
        if not self.verify_not_attribute(attr_, value_, msg):
            raise AssertionError

    def assert_css_class(self, class_name_, msg: Optional[str] = '') -> None:
        if not self.verify_css_class(class_name_, msg):
            raise AssertionError

    def assert_not_css_class(self, class_name_, msg: Optional[str] = '') -> None:
        if not self.verify_not_css_class(class_name_, msg):
            raise AssertionError

    def assert_css_style(self, style_name_, value_, msg: Optional[str] = '') -> None:
        if not self.verify_css_style(style_name_, value_, msg):
            raise AssertionError

    def assert_not_css_style(self, style_name_, value_, msg: Optional[str] = '') -> None:
        if not self.verify_not_css_style(style_name_, value_, msg):
            raise AssertionError

    def is_present(self) -> bool:
        try:
            if self._id != -1 and self.cacheable:
                return True

            if self._parent_element is not None:
                if not self._parent_element.is_present():
                    return False
                else:
                    elements = self._parent_element.find_elements(by=self.by, value=self.locator)
            else:
                elements = self._parent.find_elements(by=self.by, value=self.locator)

            if elements is not None and len(elements) > 0:
                if self._id == -1:
                    self._id = elements[0].id
                return True
            else:
                return False
        except:
            return False

    def _execute(self, command: str, params: dict = None) -> dict:
        command_tracker = CommandTracker(command, params)

        if params is None:
            params = {}

        if self.id != -1:
            params['id'] = self.id
        else:
            driver_command = Command.FIND_ELEMENT
            parameters = {"using": self.by, "value": self.locator, "id": -1}
            element = self.parent.execute(driver_command, parameters)['value']
            self._id = element._id
            params['id'] = self.id

        command_tracker.parameters = params
        self.before_command(command_tracker)
        try:
            if command_tracker.response is None:
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response

            self.after_command(command_tracker)
        except Exception as e:
            command_tracker.exception = e
            self.on_exception(command_tracker)

        if command_tracker.has_exception():
            if command_tracker.retry:
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response
            else:
                raise command_tracker.exception

        return command_tracker.response

    @staticmethod
    def report(operation: str, outcome: bool, msg: str, **kwargs) -> None:
        key = "element." + operation + "." + ("pass" if outcome else "fail")
        message_format = CM().get_str_for_key(key)

        not_op_pass_format = "Expected %(expected)s not {operation} : " \
                             "Actual %(actual)s not {operation}"
        not_op_fail_format = "Expected %(expected)s not {operation} : " \
                             "Actual %(actual)s {operation}"
        op_pass_format = "Expected %(expected)s {operation} : " \
                         "Actual %(actual)s {operation}"
        op_fail_format = "Expected %(expected)s {operation} : " \
                         "Actual %(actual)s not {operation}"

        not_op_val_format = "Expected %(op)s {operation} should not be %(expected)s : " \
                            "Actual %(op)s {operation} is %(actual)s"
        op_val_format = "Expected %(op)s {operation} should be %(expected)s : " \
                        "Actual %(op)s {operation} is %(actual)s"

        if message_format is None:
            condition_1 = not_op_val_format if (kwargs is not None and len(
                kwargs) > 2) else (not_op_pass_format if outcome else not_op_fail_format)

            condition_2 = op_val_format if (kwargs is not None and len(kwargs) > 2) else (
                op_pass_format if outcome else op_fail_format)

            message_format = condition_1 if operation.startswith('not') else condition_2
            message_format = message_format.replace('{operation}', operation.replace('not', ''))

        message = message_format.format(msg)

        if kwargs is not None and len(kwargs.keys()) > 0:
            message = message % kwargs
        if outcome:
            Reporter.log_with_screenshot(message, MessageType.Pass)
        else:
            Reporter.log_with_screenshot(message, MessageType.Fail)

    def before_command(self, command_tracker: CommandTracker) -> None:
        command_tracker.stage = Stage.executing_before_method
        if self._listeners is not None:
            for listener in self._listeners:
                listener.before_command(self, command_tracker)

    def after_command(self, command_tracker: CommandTracker) -> None:
        command_tracker.stage = Stage.executing_after_method
        if self._listeners is not None:
            for listener in self._listeners:
                listener.after_command(self, command_tracker)

    def on_exception(self, command_tracker: CommandTracker) -> None:
        command_tracker.stage = Stage.executing_on_failure

        if isinstance(command_tracker.get_exception_type(), StaleElementReferenceException):
            self._id = -1
            parameters = command_tracker.parameters
            parameters['id'] = self.id
            command_tracker.exception = None
            command_tracker.stage = Stage.executing_method
            self._execute(command_tracker.command, parameters)

        if self._listeners is not None:
            if command_tracker.has_exception():
                for listener in self._listeners:
                    listener.on_exception(self, command_tracker)


def _(key: str) -> QAFWebElement:
    return QAFWebElement(key=key)
