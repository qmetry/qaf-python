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

from qaf.automation.core.qaf_exceptions import KeyNotFoundError
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from selenium.webdriver import ActionChains

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM

from qaf.automation.ui.webdriver.base_driver import BaseDriver
from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement
from qaf.automation.core.reporter import Reporter

if not CM().contains_key(key=AP.TESTING_APPROACH):
    raise KeyNotFoundError(message=AP.TESTING_APPROACH + ' e.g. behave, pytest')

if CM().get_str_for_key(key=AP.TESTING_APPROACH).lower() == 'pytest':
    from qaf.automation.formatter.py_test_report.behave_step_decorators import step
elif CM().get_str_for_key(key=AP.TESTING_APPROACH).lower() == 'behave':
    from behave import *
    use_step_matcher("re")
else:
    raise NotImplemented


@step(u"COMMENT: '(?P<value>[\S\s]+)'")
def comment(context, value):
    Reporter.log(value)


@step(u"store into '(?P<var>[\S\s]+)'")
def store_last_step_result_into(context, var):
    raise NotImplemented


@step(u"store '(?P<val>[\S\s]+)' into '(?P<var>[\S\s]+)'")
def store(context, val, var):
    CM().set_object_for_key(var, val)


@step(u"sendKeys '(?P<text>[\S\s]+)' into '(?P<loc>[\S\s]+)'")
def send_keys(context, text, loc):
    QAFWebElement(loc).send_keys(text)


@step(u"assert '(?P<loc>[\S\s]+)' is present")
def assert_present(context, loc):
    QAFWebElement(loc).assert_present()


@step(u"assert link with text '(?P<link_text>[\S\s]+)' is present")
def assert_link_with_text_present(context, link_text):
    QAFWebElement('link=' + link_text).assert_present()


@step(u"assert link with partial text '(?P<link_text>[\S\s]+)' is present")
def assert_link_with_partial_text_present(context, link_text):
    QAFWebElement('partialLink=' + link_text).assert_present()


@step(u"verify '(?P<loc>[\S\s]+)' is present")
def verify_present(context, loc):
    QAFWebElement(loc).verify_present()


@step(u"verify link with text '(?P<link_text>[\S\s]+)' is present")
def verify_link_with_text_present(context, link_text):
    QAFWebElement('link=' + link_text).verify_present()


@step(u"verify link with partial text '(?P<link_text>[\S\s]+)' is present")
def verify_link_with_partial_text_present(context, link_text):
    QAFWebElement('partialLink=' + link_text).verify_present()


@step(u"assert '(?P<loc>[\S\s]+)' is visible")
def assert_visible(context, loc):
    QAFWebElement(loc).assert_visible()


@step(u"verify '(?P<loc>[\S\s]+)' is visible")
def verify_visible(context, loc):
    QAFWebElement(loc).verify_visible()


@step(u"get '(?P<url>[\S\s]+)'")
def get(context, url):
    BaseDriver().get_driver().get(url)


@step(u"switch to '(?P<driver_name>[\S\s]+)'")
def switch_driver(context, driver_name):
    raise NotImplemented


@step(u"tear down driver")
def tear_down_driver(context):
    BaseDriver().get_driver().quit()


@step(u"switch to '(?P<name_or_index>[\S\s]+)' window")
def switch_to_window(context, name_or_index):
    if isinstance(name_or_index, int):
        windows = BaseDriver().get_driver().window_handles()
        BaseDriver().get_driver().switch_to_window(windows[name_or_index])
    else:
        BaseDriver().get_driver().switch_to_window(name_or_index)


@step(u"clear '(?P<loc>[\S\s]+)'")
def clear(context, loc):
    QAFWebElement(loc).clear()


@step(u"get text of '(?P<loc>[\S\s]+)'")
def get_text(context, loc):
    QAFWebElement(loc).text()


@step(u"submit '(?P<loc>[\S\s]+)'")
def submit(context, loc):
    QAFWebElement(loc).submit()


@step(u"click on '(?P<loc>[\S\s]+)'")
def click(context, loc):
    QAFWebElement(loc).click()


@step(u"drag '(?P<source>[\S\s]+)' and drop on '(?P<target>[\S\s]+)'")
def drag_and_drop(context, source, target):
    source_element = QAFWebElement(source)
    dest_element = QAFWebElement(target)
    ActionChains(BaseDriver().get_driver()).drag_and_drop(source_element, dest_element).perform()


@step(u"wait until '(?P<loc>[\S\s]+)' to be visible")
def wait_for_visible(context, loc):
    QAFWebElement(loc).wait_for_visible()


@step(u"wait until '(?P<loc>[\S\s]+)' not to be visible")
def wait_for_not_visible(context, loc):
    QAFWebElement(loc).wait_for_not_visible()


@step(u"wait until '(?P<loc>[\S\s]+)' to be disable")
def wait_for_disabled(context, loc):
    QAFWebElement(loc).wait_for_disabled()


@step(u"wait until '(?P<loc>[\S\s]+)' to be enable")
def wait_for_enabled(context, loc):
    QAFWebElement(loc).wait_for_enabled()


@step(u"wait until '(?P<loc>[\S\s]+)' to be present")
def wait_for_present(context, loc):
    QAFWebElement(loc).wait_for_present()


@step(u"wait until '(?P<loc>[\S\s]+)' is not present")
def wait_for_not_present(context, loc):
    QAFWebElement(loc).wait_for_not_present()


@step(u"wait until '(?P<loc>[\S\s]+)' text '(?P<text>[\S\s]+)'")
def wait_for_text(context, loc, text):
    QAFWebElement(loc).wait_for_text(text)


@step(u"wait until '(?P<loc>[\S\s]+)' text is not '(?P<text>[\S\s]+)'")
def wait_for_not_text(context, loc, text):
    QAFWebElement(loc).wait_for_not_text(text)


@step(u"wait until '(?P<loc>[\S\s]+)' to be selected")
def wait_for_selected(context, loc):
    QAFWebElement(loc).wait_for_selected()


@step(u"wait until '(?P<loc>[\S\s]+)' is not selected")
def wait_for_not_selected(context, loc):
    QAFWebElement(loc).wait_for_not_selected()


@step(u"wait until '(?P<loc>[\S\s]+)' for attribute '(?P<attr>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def wait_for_attribute(context, loc, attr, value):
    QAFWebElement(loc).wait_for_attribute(attr, value)


@step(u"wait until '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def wait_for_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).wait_for_not_attribute(attr, value)


@step(u"wait until '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def wait_for_property(context, loc, prop, value):
    QAFWebElement(loc).wait_for_attribute(prop, value)


@step(u"wait until '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def wait_for_not_property(context, loc, prop, value):
    QAFWebElement(loc).wait_for_not_attribute(prop, value)


@step(u"wait until '(?P<loc>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def wait_for_value(context, loc, value):
    QAFWebElement(loc).wait_for_value(value)


@step(u"wait until '(?P<loc>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def wait_for_not_value(context, loc, value):
    QAFWebElement(loc).wait_for_not_value(value)


@step(u"wait until '(?P<loc>[\S\s]+)' css class name is '(?P<class_name>[\S\s]+)'")
def wait_for_css_class(context, loc, class_name):
    QAFWebElement(loc).wait_for_css_class(class_name)


@step(u"wait until '(?P<loc>[\S\s]+)' css class name is not '(?P<class_name>[\S\s]+)'")
def wait_for_not_css_class(context, loc, class_name):
    QAFWebElement(loc).wait_for_not_css_class(class_name)


@step(u"verify '(?P<loc>[\S\s]+)' not present")
def verify_not_present(context, loc):
    QAFWebElement(loc).verify_not_present()


@step(u"wait until ajax call complete")
def wait_for_ajax_to_complete(context):
    BaseDriver().get_driver().wait_for_ajax()


@step(u"wait until '(?P<jstoolkit>[\S\s]+)' ajax call complete")
def wait_for_ajax_to_complete(context, jstoolkit):
    BaseDriver().get_driver().wait_for_ajax(jstoolkit=jstoolkit)


@step(u"verify '(?P<loc>[\S\s]+)' not visible")
def verify_not_visible(context, loc):
    QAFWebElement(loc).verify_not_visible()


@step(u"verify '(?P<loc>[\S\s]+)' enabled")
def verify_enabled(context, loc):
    QAFWebElement(loc).verify_enabled()


@step(u"verify '(?P<loc>[\S\s]+)' disabled")
def verify_disabled(context, loc):
    QAFWebElement(loc).verify_disabled()


@step(u"verify '(?P<loc>[\S\s]+)' text is '(?P<text>[\S\s]+)'")
def verify_text(context, loc, text):
    QAFWebElement(loc).verify_text(text)


@step(u"verify '(?P<loc>[\S\s]+)' text is not '(?P<text>[\S\s]+)'")
def verify_not_text(context, loc, text):
    QAFWebElement(loc).verify_not_text(text)


@step(u"verify '(?P<loc>[\S\s]+)' is selected")
def verify_selected(context, loc):
    QAFWebElement(loc).verify_selected()


@step(u"verify '(?P<loc>[\S\s]+)' is not selected")
def verify_not_selected(context, loc):
    QAFWebElement(loc).verify_not_selected()


@step(u"verify '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def verify_attribute(context, loc, attr, value):
    QAFWebElement(loc).verify_attribute(attr, value)


@step(u"verify '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def verify_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).verify_not_attribute(attr, value)


@step(u"verify '(?P<loc>[\S\s]+)' css class name is '(?P<class_name>[\S\s]+)'")
def verify_css_class(context, loc, class_name):
    QAFWebElement(loc).verify_css_class(class_name)


@step(u"verify '(?P<loc>[\S\s]+)' css class name is not '(?P<class_name>[\S\s]+)'")
def verify_not_css_class(context, loc, class_name):
    QAFWebElement(loc).verify_not_css_class(class_name)


@step(u"verify '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def verify_property(context, loc, prop, value):
    QAFWebElement(loc).verify_attribute(prop, value)


@step(u"verify '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def verify_not_property(context, loc, prop, value):
    QAFWebElement(loc).verify_not_attribute(prop, value)


@step(u"verify '(?P<loc>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def verify_value(context, loc, value):
    QAFWebElement(loc).verify_value(value)


@step(u"verify '(?P<loc>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def verify_not_value(context, loc, value):
    QAFWebElement(loc).verify_not_value(value)


@step(u"assert '(?P<loc>[\S\s]+)' is not present")
def assert_not_present(context, loc):
    QAFWebElement(loc).assert_not_present()


@step(u"assert '(?P<loc>[\S\s]+)' is not visible")
def assert_not_visible(context, loc):
    QAFWebElement(loc).assert_not_visible()


@step(u"assert '(?P<loc>[\S\s]+)' is enable")
def assert_enabled(context, loc):
    QAFWebElement(loc).assert_enabled()


@step(u"assert '(?P<loc>[\S\s]+)' is disable")
def assert_disable(context, loc):
    QAFWebElement(loc).assert_disabled()


@step(u"assert '(?P<loc>[\S\s]+)' text is '(?P<text>[\S\s]+)'")
def assert_text(context, loc, text):
    QAFWebElement(loc).assert_text(text)


@step(u"assert '(?P<loc>[\S\s]+)' text is not '(?P<text>[\S\s]+)'")
def assert_not_text(context, loc, text):
    QAFWebElement(loc).assert_not_text(text)


@step(u"assert '(?P<loc>[\S\s]+)' is not selected")
def assert_selected(context, loc):
    QAFWebElement(loc).assert_not_selected()


@step(u"assert '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def assert_attribute(context, loc, attr, value):
    QAFWebElement(loc).assert_attribute(attr, value)


@step(u"assert '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def assert_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).assert_not_attribute(attr, value)


@step(u"assert '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def assert_property(context, loc, prop, value):
    QAFWebElement(loc).assert_attribute(prop, value)


@step(u"assert '(?P<loc>[\S\s]+)' property '(?P<prop>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def assert_not_property(context, loc, prop, value):
    QAFWebElement(loc).assert_not_attribute(prop, value)


@step(u"assert '(?P<loc>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def assert_value(context, loc, value):
    QAFWebElement(loc).assert_value(value)


@step(u"assert '(?P<loc>[\S\s]+)' value is not '(?P<value>[\S\s]+)'")
def assert_not_value(context, loc, value):
    QAFWebElement(loc).assert_not_value(value)


@step(u"assert '(?P<loc>[\S\s]+)' css class name is '(?P<class_name>[\S\s]+)'")
def assert_css_class(context, loc, class_name):
    QAFWebElement(loc).assert_css_class(class_name)


@step(u"assert '(?P<loc>[\S\s]+)' css class name is not '(?P<class_name>[\S\s]+)'")
def assert_not_css_class(context, loc, class_name):
    QAFWebElement(loc).assert_not_css_class(class_name)


@step(u"set '(?P<loc>[\S\s]+)' attribute '(?P<attr>[\S\s]+)' value is '(?P<value>[\S\s]+)'")
def set_attribute(context, loc, attr, value):
    element = QAFWebElement(loc)
    BaseDriver().get_driver().execute_script("arguments[0].{attr} = arguments[1]".format(attr=attr), element, value)


@step(u"add cookie '(?P<name>[\S\s]+)' with value '(?P<value>[\S\s]+)'")
def add_cookie(context, name, value):
    BaseDriver().get_driver().add_cookie({name: value})


@step(u"delete cookie with name '(?P<name>[\S\s]+)'")
def delete_cookie(context, name):
    BaseDriver().get_driver().delete_cookie(name)


@step(u"delete all cookies")
def delete_all_cookies(context):
    BaseDriver().get_driver().delete_all_cookies()


@step(u"get a cookie with a name '(?P<name>[\S\s]+)'")
def get_cookie(context, name):
    BaseDriver().get_driver().get_cookie(name)


@step(u"mouse move on '(?P<loc>[\S\s]+)'")
def mouse_move(context, loc):
    location = QAFWebElement(loc).location
    ActionChains(BaseDriver().get_driver()).move_by_offset(location['x'], location['y'])


@step(u"switch to frame '(?P<frame_name>[\s\S]+)'")
def switch_frame(context, frame_name):
    BaseDriver().get_driver().switch_to_frame(frame_name)


@step(u"switch to parent frame")
def switch_to_parent_frame(context):
    BaseDriver().get_driver().switch_to_default_content()
