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
import time
from typing import Any
from typing import Optional

from hamcrest import contains_string
from hamcrest.core.matcher import Matcher
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.core.message_type import MessageType
from qaf.automation.core.reporter import Reporter
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.util.dynamic_wait import DynamicWait
from qaf.automation.ui.util.locator_util import parse_locator
from qaf.automation.ui.util.qaf_element_expected_conditions import ElementToBeVisible, ElementToBeEnabled, \
    PresenceOfElement, ElementHasText, ElementTextMatches, ElementHasValue, \
    ElementValueMatches, ElementToBeSelected, ElementHasAttribute, ElementAttributeMatches, \
    ElementHasCssClass, ElementHasCssStyle, ElementCssClassMatches, ElementCssStyleMatches
from qaf.automation.ui.webdriver.command_tracker import Stage, CommandTracker


class QAFWebElement(RemoteWebElement):
    def __init__(self, locator: str, parent_locator: Optional[str] = '',
                 cacheable: Optional[bool] = False, **kwargs) -> None:

        self.locator = None
        self.by = None
        self.description = None
        self._parent_element = QAFWebElement(parent_locator) if len(parent_locator) > 0 else None
        self._listeners = []
        self.cacheable = cacheable
        self.metadata = {}

        if len(locator) > 0:
            from qaf.automation.core.test_base import get_driver
            parent = get_driver()
            value = CM.get_bundle().get_raw_value(locator, locator)
            value = CM.get_bundle().resolve(value, kwargs)
            self.by, self.locator, self.description, self.metadata = parse_locator(value)
            self.cacheable = self.cacheable or self.metadata.get("cacheable", False)
            self._id = -1
            RemoteWebElement.__init__(self, parent=parent, id_=self._id)

        if CM.get_bundle().contains_key(AP.WEBELEMENT_COMMAND_LISTENERS):
            class_name = CM.get_bundle().get_string(AP.WEBELEMENT_COMMAND_LISTENERS)
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
        # cls._w3c = remote_webelement._w3c
        return cls(locator='')

    def get_description(self, msg: Optional[str] = '') -> str:
        return msg if len(msg) > 0 else self.description

    def find_element(self, by: Optional[str] = By.ID, value: Optional[str] = None):
        web_element = super(QAFWebElement, self).find_element(by=by, value=value)
        qaf_web_element = QAFWebElement.create_instance_using_webelement(web_element)
        qaf_web_element._parent_element = self
        qaf_web_element._parent = self
        qaf_web_element._id = web_element.id
        qaf_web_element.by = by
        qaf_web_element.locator = value
        qaf_web_element.description = value
        qaf_web_element.cacheable = True
        return qaf_web_element

    def find_elements(self, by: Optional[str] = By.ID, value: Optional[str] = None):
        web_elements = super(QAFWebElement, self).find_elements(by=by, value=value)
        qaf_web_elements = []
        for web_element in web_elements:
            qaf_web_element = QAFWebElement.create_instance_using_webelement(web_element)
            qaf_web_element._parent_element = self
            qaf_web_element._parent = self
            qaf_web_element._id = web_element.id
            qaf_web_element.by = by
            qaf_web_element.locator = value
            qaf_web_element.description = value
            qaf_web_element.cacheable = True
            qaf_web_elements.append(qaf_web_element)
        return qaf_web_elements

    def wait_for_visible(self, wait_time: Optional[int] = 0) -> bool:
        message = 'Wait time out for ' + self.description + ' to be visible'
        return qaf_web_element_wait(self, wait_time).until(ElementToBeVisible(), message)

    def wait_for_not_visible(self, wait_time: Optional[int] = 0) -> bool:
        message = 'Wait time out for ' + self.description + ' to be not visible'
        return qaf_web_element_wait(self, wait_time).until_not(ElementToBeVisible(), message)

    def wait_for_disabled(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " to be disabled"
        return qaf_web_element_wait(self, wait_time).until_not(ElementToBeEnabled(), message)

    def wait_for_enabled(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " to be enabled"
        return qaf_web_element_wait(self, wait_time).until(ElementToBeEnabled(), message)

    def wait_for_present(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " to be present"
        return qaf_web_element_wait(self, wait_time).until(PresenceOfElement(), message)

    def wait_for_not_present(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " to not be present"
        return qaf_web_element_wait(self, wait_time).until_not(PresenceOfElement(), message)

    def wait_for_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " text " + text_
        return qaf_web_element_wait(self, wait_time).until(ElementHasText(text_), message)

    def wait_for_matches_text(self, text_matcher: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} text matches {text_matcher}'
        return qaf_web_element_wait(self, wait_time).until(ElementTextMatches(text_matcher), message)

    def wait_for_not_text(self, text_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " text not " + text_
        return qaf_web_element_wait(self, wait_time).until_not(ElementHasText(text_), message)

    def wait_for_not_matches_text(self, text_matcher: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} containing text not {text_matcher}'
        return qaf_web_element_wait(self, wait_time).until_not(ElementTextMatches(text_matcher), message)

    def wait_for_value(self, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " value " + value_
        return qaf_web_element_wait(self, wait_time).until(ElementHasValue(value_), message)

    def wait_for_not_value(self, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " value not " + value_
        return qaf_web_element_wait(self, wait_time).until_not(ElementHasValue(value_), message)

    def wait_for_value_matches(self, value_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} value {value_}'
        return qaf_web_element_wait(self, wait_time).until(ElementValueMatches(value_), message)

    def wait_for_not_value_matches(self, value_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} value not {value_}'
        return qaf_web_element_wait(self, wait_time).until_not(ElementValueMatches(value_), message)

    def wait_for_selected(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " to be selected"
        return qaf_web_element_wait(self, wait_time).until(ElementToBeSelected(), message)

    def wait_for_not_selected(self, wait_time: Optional[int] = 0) -> bool:
        message = "Wait time out for " + self.description + " not to be selected"
        return qaf_web_element_wait(self, wait_time).until_not(ElementToBeSelected(), message)

    def wait_for_attribute(self, attr_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " " + attr_ + " = " + value_
        return qaf_web_element_wait(self, wait_time).until(ElementHasAttribute(attr_, value_), message)

    def wait_for_not_attribute(self, attr_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " " + attr_ + " != " + value_
        return qaf_web_element_wait(self, wait_time).until_not(ElementHasAttribute(attr_, value_), message)

    def wait_for_attribute_matches(self, attr_: str, value_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} {attr_} {value_}'
        return qaf_web_element_wait(self, wait_time).until(ElementAttributeMatches(attr_, value_), message)

    def wait_for_not_attribute_matches(self, attr_: str, value_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} {attr_} not {value_}'
        return qaf_web_element_wait(self, wait_time).until_not(ElementAttributeMatches(attr_, value_), message)

    def wait_for_css_class(self, class_name_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " have css class " + class_name_
        return qaf_web_element_wait(self, wait_time).until(ElementHasCssClass(class_name_), message)

    def wait_for_not_css_class(self, class_name_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " have not css class " + class_name_
        return qaf_web_element_wait(self, wait_time).until_not(ElementHasCssClass(class_name_), message)

    def wait_for_css_class_matches(self, class_name_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} have css class {class_name_}'
        return qaf_web_element_wait(self, wait_time).until(ElementCssClassMatches(class_name_), message)

    def wait_for_not_css_class_matches(self, class_name_: Matcher, wait_time: Optional[int] = 0) -> (bool, Any):
        message = f'Wait time out for {self.description} have not css class {class_name_}'
        return qaf_web_element_wait(self, wait_time).until_not(ElementCssClassMatches(class_name_), message)

    def wait_for_css_style(self, style_name_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " have css style " + style_name_ + "=" + value_
        return qaf_web_element_wait(self, wait_time).until(ElementHasCssStyle(style_name_, value_), message)

    def wait_for_not_css_style(self, style_name_: str, value_: str, wait_time: Optional[int] = 0) -> (bool, Any):
        message = "Wait time out for " + self.description + " have not css style " + style_name_ + "=" + value_
        return qaf_web_element_wait(self, wait_time).until_not(ElementHasCssStyle(style_name_, value_), message)

    def wait_for_css_style_matches(self, style_name_: str, value_: Matcher, wait_time: Optional[int] = 0) -> (
            bool, Any):
        message = f'Wait time out for {self.description} have css style {style_name_} {value_}'
        return qaf_web_element_wait(self, wait_time).until(ElementCssStyleMatches(style_name_, value_), message)

    def wait_for_not_css_style_matches(self, style_name_: str, value_: Matcher, wait_time: Optional[int] = 0) -> (
            bool, Any):
        message = f'Wait time out for {self.description} have not css style {style_name_} {value_}'
        return qaf_web_element_wait(self, wait_time).until_not(ElementCssStyleMatches(style_name_, value_),
                                                               message)

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
            return_value = ElementHasText(text_)(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
        self.report("text", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_text_contain(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_matches_text(contains_string(text_))
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            return_value = ElementTextMatches(contains_string(text_))(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasText(text_)(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
        self.report("nottext", outcome, msg, expected=text_, actual=actaul_)
        return outcome

    def verify_not_text_contains(self, text_: str, msg: Optional[str] = '') -> bool:
        if not self.__ensure_present(msg):
            return False

        actaul_ = ''
        msg = self.get_description(msg)
        try:
            return_value = self.wait_for_not_matches_text(contains_string(text_))
            outcome = return_value[0]
            actaul_ = return_value[1]
        except TimeoutException:
            return_value = ElementTextMatches(contains_string(text_))(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasValue(value_)(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasValue(value_)(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasAttribute(attr_, value_)(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasAttribute(attr_, value_)(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasCssClass(class_name_)(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasCssClass(class_name_)(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasCssStyle(style_name_, value_)(self)
            outcome = return_value[0]
            actaul_ = return_value[1]
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
            return_value = ElementHasCssStyle(style_name_, value_)(self)
            outcome = not return_value[0]
            actaul_ = return_value[1]
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
        self.load()
        params['id'] = self._id

        command_tracker.parameters = params
        self.before_command(command_tracker)
        try:
            if command_tracker.response is None:
                command_tracker.start_time = round(time.time() * 1000)
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response
                command_tracker.end_time = round(time.time() * 1000)
            self.after_command(command_tracker)
        except Exception as e:
            command_tracker.exception = e
            command_tracker.end_time = round(time.time() * 1000)
            self.on_exception(command_tracker)

        if command_tracker.has_exception():
            if command_tracker.retry:
                response = self.parent.execute(command_tracker.command,
                                               command_tracker.parameters)
                command_tracker.response = response
            else:
                raise command_tracker.exception

        return command_tracker.response

    def load(self):
        if self._id == -1:
            parameters = {"using": self.by, "value": self.locator, "id": self._id}
            command_tracker = CommandTracker(Command.FIND_ELEMENT, parameters)
            if self._parent_element is None:
                self.before_command(command_tracker)
                self._id = self.parent.load(self)
                self.after_command(command_tracker)
            else:
                self._parent_element.load()
                self.before_command(command_tracker)
                self._id = self._parent_element.find_element(by=self.by, value=self.locator).id
                self.after_command(command_tracker)

    @staticmethod
    def report(operation: str, outcome: bool, msg: str, **kwargs) -> None:
        key = "element." + operation + "." + ("pass" if outcome else "fail")
        message_format = CM.get_bundle().get_string(key)

        not_op_pass_format = "Expected \"{0}\" should not be {operation} : " \
                             "Actual was not {operation}"
        not_op_fail_format = "Expected \"{0}\" should not be {operation} : " \
                             "Actual was {operation}"
        op_pass_format = "Expected  \"{0}\" should  be {operation}: " \
                         "Actual was {operation}"
        op_fail_format = "Expected \"{0}\" should be {operation} : " \
                         "Actual was not {operation}"

        not_op_val_format = "Expected \"{0}\" %(op)s {operation} should not be \"%(expected)s\" : " \
                            "Actual was \"%(actual)s\""
        op_val_format = "Expected \"{0}\" %(op)s {operation} should be \"%(expected)s\" : " \
                        "Actual was \"%(actual)s\""

        if message_format is None:
            condition_1 = not_op_val_format if (kwargs is not None and len(
                kwargs) >= 2) else (not_op_pass_format if outcome else not_op_fail_format)

            condition_2 = op_val_format if (kwargs is not None and len(kwargs) >= 2) else (
                op_pass_format if outcome else op_fail_format)

            message_format = condition_1 if operation.startswith('not') else condition_2
            message_format = message_format.replace('{operation}', operation.replace('not', ''))

        message = message_format.format(msg)

        if kwargs is not None and len(kwargs.keys()) > 0:
            if "op" not in kwargs:
                kwargs["op"] = ""
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


def qaf_web_element_wait(ele: QAFWebElement, timeout, ignored_exceptions=None) -> \
        DynamicWait[QAFWebElement]:
    return DynamicWait[QAFWebElement](ele, timeout, ignored_exceptions=ignored_exceptions)


def _(locator: str, parent_locator: Optional[str] = '',
      cacheable: Optional[bool] = True, **kwargs) -> QAFWebElement:
    return QAFWebElement(locator=locator, parent_locator=parent_locator, cacheable=cacheable, **kwargs)
