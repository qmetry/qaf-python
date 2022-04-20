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

from selenium.webdriver.common.by import By


def get_find_by(locator: str) -> (str, str):
    if locator.startswith('xpath='):
        by = By.XPATH
        value = locator.split('xpath=', 1)[1]
    elif locator.startswith('//'):
        by = By.XPATH
        value = locator
    elif locator.startswith('id='):
        by = By.XPATH
        value = "//*[@id='" + locator.split('id=', 1)[1] + "']"
    elif locator.startswith('name='):
        by = By.XPATH
        value = "//*[@name='" + locator.split('name=', 1)[1] + "']"
    elif locator.startswith('class='):
        by = By.XPATH
        value = "//*[@class='" + locator.split('class=', 1)[1] + "']"
    elif locator.startswith('text='):
        by = By.XPATH
        value = "//*[@text='" + locator.split('text=', 1)[1] + "']"
    elif locator.startswith('content-desc='):
        by = By.XPATH
        value = '//*[@*="' + locator.split('content-desc=', 1)[1] + '"]'
    elif "=" in locator:
        by = str(locator).split("=")[0]
        value = str(locator).split("=")[1]
    else:
        by = By.ID
        value = str(locator)
    return by, value
