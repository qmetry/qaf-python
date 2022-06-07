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
from selenium.webdriver.common.by import By


def get_find_by(locator: str, w3c=False) -> (str, str):
    if locator.startswith('xpath='):
        return By.XPATH, locator.split('xpath=', 1)[1]
    elif locator.startswith('//'):
        return By.XPATH, locator
    elif locator.startswith('css='):
        return By.CSS_SELECTOR, locator.split('css=', 1)[1]
    elif locator.startswith('text='):
        return By.LINK_TEXT, locator.split('text=', 1)[1]

    if w3c:
        if locator.startswith('id='):
            return By.CSS_SELECTOR, '[id="%s"]' % locator.split('id=', 1)[1]
        elif locator.startswith('name='):
            return By.CSS_SELECTOR, '[name="%s"]' % locator.split('name=', 1)[1]
        elif locator.startswith('class='):
            return By.CSS_SELECTOR, ".%s" % locator.split('class=', 1)[1]
        elif locator.startswith('tag='):
            return By.CSS_SELECTOR, locator.split('tag=', 1)[1]
    else:
        if locator.startswith('id='):
            return By.ID, locator.split('id=', 1)[1]
        elif locator.startswith('name='):
            return By.NAME, locator.split('name=', 1)[1]
        elif locator.startswith('class='):
            return By.CLASS_NAME, locator.split('class=', 1)[1]
        elif locator.startswith('tag='):
            return By.TAG_NAME, locator.split('tag=', 1)[1]

    if "=" in locator:
        return str(locator).split("=")[0], str(locator).split("=")[1]
    else:
        return By.CSS_SELECTOR, '[id="%s"]' % locator
