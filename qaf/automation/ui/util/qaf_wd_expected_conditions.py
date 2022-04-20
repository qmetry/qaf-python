#  Copyright (c) .2022 Infostretch Corporation
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

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException


class WaitForAjax(object):
    def __init__(self, snippet: str) -> None:
        self.snippet = snippet

    def __call__(self, driver) -> bool:
        try:
            value = driver.execute_script(self.snippet)
            return bool(value)
        except StaleElementReferenceException:
            return False


class WaitForVisible(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            value = _find_element(driver, self.locator).is_displayed()
            return value
        except StaleElementReferenceException:
            return False


class WaitForNotVisible(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            value = _find_element(driver, self.locator).is_displayed()
            return not value
        except StaleElementReferenceException:
            return False


class WaitForDisabled(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            value = _find_element(driver, self.locator).is_enabled()
            return not value
        except StaleElementReferenceException:
            return False


class WaitForEnabled(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            value = _find_element(driver, self.locator).is_enabled()
            return value
        except StaleElementReferenceException:
            return False


class WaitForPresent(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            elements = _find_elements(driver, self.locator)
            if elements is not None and len(elements) > 0:
                return True
            else:
                return False
        except NoSuchElementException as e:
            return False


class WaitForNotPresent(object):
    def __init__(self, locator: (str, str)) -> None:
        self.locator = locator

    def __call__(self, driver) -> bool:
        try:
            elements = _find_elements(driver, self.locator)
            if elements is None:
                return True
            else:
                return False
        except NoSuchElementException as e:
            return True


class WaitForText(object):
    def __init__(self, locator: (str, str), text_: str) -> None:
        self.locator = locator
        self.text = text_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_text = _find_element(driver, self.locator).text
            return self.text == element_text, element_text
        except StaleElementReferenceException:
            return False, None


class WaitForContainingText(object):
    def __init__(self, locator: (str, str), text_: str) -> None:
        self.locator = locator
        self.text = text_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_text = _find_element(driver, self.locator).text
            return self.text in element_text, element_text
        except StaleElementReferenceException:
            return False, None


class WaitForNotText(object):
    def __init__(self, locator: (str, str), text_: str) -> None:
        self.locator = locator
        self.text = text_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_text = _find_element(driver, self.locator).text
            return self.text != element_text, element_text
        except StaleElementReferenceException:
            return False, None


class WaitForNotContainingText(object):
    def __init__(self, locator: (str, str), text_: str) -> None:
        self.locator = locator
        self.text = text_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_text = _find_element(driver, self.locator).text
            return self.text not in element_text, element_text
        except StaleElementReferenceException:
            return False, None


class WaitForValue(object):
    def __init__(self, locator: (str, str), value_: str) -> None:
        self.locator = locator
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_value = _find_element(driver, self.locator).get_attribute("value")
            return self.value == element_value, element_value
        except StaleElementReferenceException:
            return False, None


class WaitForNotValue(object):
    def __init__(self, locator: (str, str), value_: str) -> None:
        self.locator = locator
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_value = _find_element(driver, self.locator).get_attribute("value")
            return self.value != element_value, element_value
        except StaleElementReferenceException:
            return False, None


class WaitForSelected(object):
    def __init__(self, element) -> None:
        self.element = element

    def __call__(self, ignored) -> bool:
        return self.element.is_selected()


class WaitForNotSelected(object):
    def __init__(self, element) -> None:
        self.element = element

    def __call__(self, ignored) -> bool:
        return not self.element.is_selected()


class WaitForAttribute(object):
    def __init__(self, locator: (str, str), attr_: str, value_: str) -> None:
        self.attr = attr_
        self.locator = locator
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_value = _find_element(driver, self.locator).get_attribute(self.attr)
            return self.value == element_value, element_value
        except StaleElementReferenceException:
            return False, None


class WaitForNotAttribute(object):
    def __init__(self, locator: (str, str), attr_: str, value_: str) -> None:
        self.attr = attr_
        self.locator = locator
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_value = _find_element(driver, self.locator).get_attribute(self.attr)
            return self.value != element_value, element_value
        except StaleElementReferenceException:
            return False, None


class WaitForCssClass(object):
    def __init__(self, locator: (str, str), class_name_: str) -> None:
        self.locator = locator
        self.class_name = class_name_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_class = _find_element(driver, self.locator).get_attribute("class")
            return self.class_name == element_class, element_class
        except StaleElementReferenceException:
            return False, None


class WaitForNotCssClass(object):
    def __init__(self, locator: (str, str), class_name_: str) -> None:
        self.locator = locator
        self.class_name = class_name_

    def __call__(self, driver) -> (bool, Any):
        try:
            element_class = _find_element(driver, self.locator).get_attribute("class")
            return self.class_name != element_class, element_class
        except StaleElementReferenceException:
            return False, None


class WaitForCssStyle(object):
    def __init__(self, locator: (str, str), style_name_: str, value_: str) -> None:
        self.locator = locator
        self.style_name = style_name_
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            style_value = _find_element(driver, self.locator).value_of_css_property(self.value)
            return self.style_name == style_value, style_value
        except StaleElementReferenceException:
            return False, None


class WaitForNotCssStyle(object):
    def __init__(self, locator: (str, str), style_name_: str, value_: str) -> None:
        self.locator = locator
        self.style_name = style_name_
        self.value = value_

    def __call__(self, driver) -> (bool, Any):
        try:
            style_value = _find_element(driver, self.locator).get_attribute(self.value)
            return self.style_name != style_value, style_value
        except StaleElementReferenceException:
            return False, None


def _find_element(driver, by: tuple):
    try:
        return driver.find_element(*by)
    except NoSuchElementException as e:
        raise e
    except WebDriverException as e:
        raise e


def _find_elements(driver, by: tuple):
    try:
        return driver.find_elements(*by)
    except WebDriverException as e:
        raise e
