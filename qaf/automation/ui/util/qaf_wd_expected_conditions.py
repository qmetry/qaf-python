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

from selenium.common.exceptions import NoSuchElementException


class WaitForAjax(object):
    def __init__(self, snippet: str) -> None:
        self.snippet = snippet

    def __call__(self, driver) -> bool:
        try:
            value = driver.execute_script(self.snippet)
            return bool(value)
        except:
            return False


class WaitForAnyPresent(object):
    def __init__(self, locators: [str]) -> None:
        self.locators = locators

    def __call__(self, driver) -> bool:
        try:
            from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement
            for locator in self.locators:
                if QAFWebElement(locator=locator).is_present():
                    return True
            return False
        except NoSuchElementException:
            return False
