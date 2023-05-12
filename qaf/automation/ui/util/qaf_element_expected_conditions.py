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


from typing import Any

from hamcrest import equal_to, starts_with, ends_with, contains_string, equal_to_ignoring_case, matches_regexp
from hamcrest.core.matcher import Matcher
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

"""
@Author: Chirag Jayswal
Collection of different element conditions that can be used with DymamicWait[QAFWebElement].
"""


class ElementToBeVisible(object):
    def __call__(self, element) -> bool:
        try:
            value = element.is_displayed()
            return value
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            element._id = -1
            return False


class ElementToBeEnabled(object):
    def __call__(self, element) -> bool:
        try:
            value = element.is_enabled()
            return value
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            element._id = -1
            return False


class PresenceOfElement(object):
    def __call__(self, element) -> bool:
        try:
            return element.is_present()
        except NoSuchElementException:
            return False


class ElementTextMatches(object):
    def __init__(self, matcher_: Matcher) -> None:
        self.matcher = matcher_

    def __call__(self, element) -> (bool, Any):
        try:
            element_text = element.text
            return self.matcher.matches(element_text), element_text
        except NoSuchElementException:
            return False, None
        except StaleElementReferenceException:
            element._id = -1
            return False, None


def ElementHasText(value: str) -> ElementTextMatches:
    return ElementTextMatches(to_matcher(value))


class ElementValueMatches(object):
    def __init__(self, value_: Matcher) -> None:
        self.matcher = value_

    def __call__(self, element) -> (bool, Any):
        try:
            element_value = element.get_attribute("value")
            return self.matcher.matches(element_value), element_value
        except NoSuchElementException:
            return False, None
        except StaleElementReferenceException:
            element._id = -1
            return False, None


def ElementHasValue(value: str) -> ElementValueMatches:
    return ElementValueMatches(to_matcher(value))


class ElementToBeSelected(object):

    def __call__(self, element) -> bool:
        try:
            value = element.is_selected()
            return value
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            element._id = -1
            return False


class ElementAttributeMatches(object):
    def __init__(self, attr_: str, matcher_: Matcher) -> None:
        self.attr = attr_
        self.matcher = matcher_

    def __call__(self, element) -> (bool, Any):
        try:
            element_value = element.get_attribute(self.attr)
            return self.matcher.matches(element_value), element_value
        except NoSuchElementException:
            return False, None
        except StaleElementReferenceException:
            element._id = -1
            return False, None


def ElementHasAttribute(attr_: str, value: str) -> ElementAttributeMatches:
    return ElementAttributeMatches(attr_, to_matcher(value))


class ElementCssClassMatches(object):
    def __init__(self, class_name_mathcher_: Matcher) -> None:
        self.class_name_mathcher = class_name_mathcher_

    def __call__(self, element) -> (bool, Any):
        try:
            element_class = element.get_attribute("class")
            return self.class_name_mathcher.matches(element_class), element_class
        except NoSuchElementException:
            return False, None
        except StaleElementReferenceException:
            element._id = -1
            return False, None


def ElementHasCssClass(value: str) -> ElementCssClassMatches:
    return ElementCssClassMatches(to_matcher(value))


class ElementCssStyleMatches(object):
    def __init__(self, style_name_: str, value_: Matcher) -> None:
        self.style_name = style_name_
        self.value = value_

    def __call__(self, element) -> (bool, Any):
        try:
            style_value = element.value_of_css_property(self.style_name)
            return self.value.matches(style_value), style_value
        except NoSuchElementException:
            return False, None
        except StaleElementReferenceException:
            element._id = -1
            return False, None


def ElementHasCssStyle(style_name_: str, value: str) -> ElementCssStyleMatches:
    return ElementCssStyleMatches(style_name_, to_matcher(value))


def to_matcher(value: str) -> Matcher:
    kv = value.split(":", 1)
    if len(kv) == 1:
        return equal_to(value)
    matchers = {"eq": equal_to, "start": starts_with, "end": ends_with, "in": contains_string,
                "exactIgnoringCase": equal_to_ignoring_case, "exact": equal_to, "like": matches_regexp}
    _matcher = matchers.get(kv[0], None)
    return _matcher(kv[1]) if _matcher is not None else equal_to(value)
