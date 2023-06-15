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

from selenium.webdriver import ActionChains

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.qaf_exceptions import KeyNotFoundError
from qaf.automation.core.reporter import Reporter
from qaf.automation.core.test_base import get_driver
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement

if not CM().contains_key(key=AP.TESTING_APPROACH):
    raise KeyNotFoundError(message=AP.TESTING_APPROACH + ' e.g. behave, pytest')

if CM().get_str_for_key(key=AP.TESTING_APPROACH).lower() == 'pytest':
    from qaf.automation.bdd2.step_registry import step
elif CM().get_str_for_key(key=AP.TESTING_APPROACH).lower() == 'behave':
    from behave import step
else:
    raise NotImplemented


#use_step_matcher("re")


@step(u"COMMENT: '{value}'")
def comment(context, value):
    Reporter.log(value)


@step(u"store into '{var}'")
def store_last_step_result_into(context, var):
    raise NotImplemented


@step(u"store '{val}' into '{var}'")
def store(context, val, var):
    CM().set_object_for_key(var, val)


@step(u"sendKeys '{text}' into '{loc}'")
def send_keys(context, text, loc):
    QAFWebElement(loc).send_keys(text)


@step(u"assert '{loc}' is present")
def assert_present(context, loc):
    QAFWebElement(loc).assert_present()


@step(u"assert link with text '{link_text}' is present")
def assert_link_with_text_present(context, link_text):
    QAFWebElement('link=' + link_text).assert_present()


@step(u"assert link with partial text '{link_text}' is present")
def assert_link_with_partial_text_present(context, link_text):
    QAFWebElement('partialLink=' + link_text).assert_present()


@step(u"verify '{loc}' is present")
def verify_present(context, loc):
    QAFWebElement(loc).verify_present()


@step(u"verify link with text '{link_text}' is present")
def verify_link_with_text_present(context, link_text):
    QAFWebElement('link=' + link_text).verify_present()


@step(u"verify link with partial text '{link_text}' is present")
def verify_link_with_partial_text_present(context, link_text):
    QAFWebElement('partialLink=' + link_text).verify_present()


@step(u"assert '{loc}' is visible")
def assert_visible(context, loc):
    QAFWebElement(loc).assert_visible()


@step(u"verify '{loc}' is visible")
def verify_visible(context, loc):
    QAFWebElement(loc).verify_visible()


@step(u"get '{url}'")
def get(context, url):
    get_driver().get(url)


@step(u"switch to '{driver_name}'")
def switch_driver(context, driver_name):
    raise NotImplemented


@step(u"tear down driver")
def tear_down_driver(context):
    get_driver().quit()


@step(u"switch to '{name_or_index}' window")
def switch_to_window(context, name_or_index):
    if isinstance(name_or_index, int):
        windows = get_driver().window_handles()
        get_driver().switch_to_window(windows[name_or_index])
    else:
        get_driver().switch_to_window(name_or_index)


@step(u"clear '{loc}'")
def clear(context, loc):
    QAFWebElement(loc).clear()


@step(u"get text of '{loc}'")
def get_text(context, loc):
    QAFWebElement(loc).text()


@step(u"submit '{loc}'")
def submit(context, loc):
    QAFWebElement(loc).submit()


@step(u"click on '{loc}'")
def click(context, loc):
    QAFWebElement(loc).click()


@step(u"drag '{source}' and drop on '{target}'")
def drag_and_drop(context, source, target):
    source_element = QAFWebElement(source)
    dest_element = QAFWebElement(target)
    ActionChains(get_driver()).drag_and_drop(source_element, dest_element).perform()


@step(u"wait until '{loc}' to be visible")
def wait_for_visible(context, loc):
    QAFWebElement(loc).wait_for_visible()


@step(u"wait until '{loc}' not to be visible")
def wait_for_not_visible(context, loc):
    QAFWebElement(loc).wait_for_not_visible()


@step(u"wait until '{loc}' to be disable")
def wait_for_disabled(context, loc):
    QAFWebElement(loc).wait_for_disabled()


@step(u"wait until '{loc}' to be enable")
def wait_for_enabled(context, loc):
    QAFWebElement(loc).wait_for_enabled()


@step(u"wait until '{loc}' to be present")
def wait_for_present(context, loc):
    QAFWebElement(loc).wait_for_present()


@step(u"wait until '{loc}' is not present")
def wait_for_not_present(context, loc):
    QAFWebElement(loc).wait_for_not_present()


@step(u"wait until '{loc}' text '{text}'")
def wait_for_text(context, loc, text):
    QAFWebElement(loc).wait_for_text(text)


@step(u"wait until '{loc}' text is not '{text}'")
def wait_for_not_text(context, loc, text):
    QAFWebElement(loc).wait_for_not_text(text)


@step(u"wait until '{loc}' to be selected")
def wait_for_selected(context, loc):
    QAFWebElement(loc).wait_for_selected()


@step(u"wait until '{loc}' is not selected")
def wait_for_not_selected(context, loc):
    QAFWebElement(loc).wait_for_not_selected()


@step(u"wait until '{loc}' for attribute '{attr}' value is '{value}'")
def wait_for_attribute(context, loc, attr, value):
    QAFWebElement(loc).wait_for_attribute(attr, value)


@step(u"wait until '{loc}' attribute '{attr}' value is not '{value}'")
def wait_for_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).wait_for_not_attribute(attr, value)


@step(u"wait until '{loc}' property '{prop}' value is '{value}'")
def wait_for_property(context, loc, prop, value):
    QAFWebElement(loc).wait_for_attribute(prop, value)


@step(u"wait until '{loc}' property '{prop}' value is not '{value}'")
def wait_for_not_property(context, loc, prop, value):
    QAFWebElement(loc).wait_for_not_attribute(prop, value)


@step(u"wait until '{loc}' value is '{value}'")
def wait_for_value(context, loc, value):
    QAFWebElement(loc).wait_for_value(value)


@step(u"wait until '{loc}' value is not '{value}'")
def wait_for_not_value(context, loc, value):
    QAFWebElement(loc).wait_for_not_value(value)


@step(u"wait until '{loc}' css class name is '{class_name}'")
def wait_for_css_class(context, loc, class_name):
    QAFWebElement(loc).wait_for_css_class(class_name)


@step(u"wait until '{loc}' css class name is not '{class_name}'")
def wait_for_not_css_class(context, loc, class_name):
    QAFWebElement(loc).wait_for_not_css_class(class_name)


@step(u"verify '{loc}' not present")
def verify_not_present(context, loc):
    QAFWebElement(loc).verify_not_present()


@step(u"wait until ajax call complete")
def wait_for_ajax_to_complete(context):
    get_driver().wait_for_ajax()


@step(u"wait until '{jstoolkit}' ajax call complete")
def wait_for_ajax_to_complete(context, jstoolkit):
    get_driver().wait_for_ajax(jstoolkit=jstoolkit)


@step(u"verify '{loc}' not visible")
def verify_not_visible(context, loc):
    QAFWebElement(loc).verify_not_visible()


@step(u"verify '{loc}' enabled")
def verify_enabled(context, loc):
    QAFWebElement(loc).verify_enabled()


@step(u"verify '{loc}' disabled")
def verify_disabled(context, loc):
    QAFWebElement(loc).verify_disabled()


@step(u"verify '{loc}' text is '{text}'")
def verify_text(context, loc, text):
    QAFWebElement(loc).verify_text(text)


@step(u"verify '{loc}' text is not '{text}'")
def verify_not_text(context, loc, text):
    QAFWebElement(loc).verify_not_text(text)


@step(u"verify '{loc}' is selected")
def verify_selected(context, loc):
    QAFWebElement(loc).verify_selected()


@step(u"verify '{loc}' is not selected")
def verify_not_selected(context, loc):
    QAFWebElement(loc).verify_not_selected()


@step(u"verify '{loc}' attribute '{attr}' value is '{value}'")
def verify_attribute(context, loc, attr, value):
    QAFWebElement(loc).verify_attribute(attr, value)


@step(u"verify '{loc}' attribute '{attr}' value is not '{value}'")
def verify_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).verify_not_attribute(attr, value)


@step(u"verify '{loc}' css class name is '{class_name}'")
def verify_css_class(context, loc, class_name):
    QAFWebElement(loc).verify_css_class(class_name)


@step(u"verify '{loc}' css class name is not '{class_name}'")
def verify_not_css_class(context, loc, class_name):
    QAFWebElement(loc).verify_not_css_class(class_name)


@step(u"verify '{loc}' property '{prop}' value is '{value}'")
def verify_property(context, loc, prop, value):
    QAFWebElement(loc).verify_attribute(prop, value)


@step(u"verify '{loc}' property '{prop}' value is not '{value}'")
def verify_not_property(context, loc, prop, value):
    QAFWebElement(loc).verify_not_attribute(prop, value)


@step(u"verify '{loc}' value is '{value}'")
def verify_value(context, loc, value):
    QAFWebElement(loc).verify_value(value)


@step(u"verify '{loc}' value is not '{value}'")
def verify_not_value(context, loc, value):
    QAFWebElement(loc).verify_not_value(value)


@step(u"assert '{loc}' is not present")
def assert_not_present(context, loc):
    QAFWebElement(loc).assert_not_present()


@step(u"assert '{loc}' is not visible")
def assert_not_visible(context, loc):
    QAFWebElement(loc).assert_not_visible()


@step(u"assert '{loc}' is enable")
def assert_enabled(context, loc):
    QAFWebElement(loc).assert_enabled()


@step(u"assert '{loc}' is disable")
def assert_disable(context, loc):
    QAFWebElement(loc).assert_disabled()


@step(u"assert '{loc}' text is '{text}'")
def assert_text(context, loc, text):
    QAFWebElement(loc).assert_text(text)


@step(u"assert '{loc}' text is not '{text}'")
def assert_not_text(context, loc, text):
    QAFWebElement(loc).assert_not_text(text)


@step(u"assert '{loc}' is not selected")
def assert_selected(context, loc):
    QAFWebElement(loc).assert_not_selected()


@step(u"assert '{loc}' attribute '{attr}' value is '{value}'")
def assert_attribute(context, loc, attr, value):
    QAFWebElement(loc).assert_attribute(attr, value)


@step(u"assert '{loc}' attribute '{attr}' value is not '{value}'")
def assert_not_attribute(context, loc, attr, value):
    QAFWebElement(loc).assert_not_attribute(attr, value)


@step(u"assert '{loc}' property '{prop}' value is '{value}'")
def assert_property(context, loc, prop, value):
    QAFWebElement(loc).assert_attribute(prop, value)


@step(u"assert '{loc}' property '{prop}' value is not '{value}'")
def assert_not_property(context, loc, prop, value):
    QAFWebElement(loc).assert_not_attribute(prop, value)


@step(u"assert '{loc}' value is '{value}'")
def assert_value(context, loc, value):
    QAFWebElement(loc).assert_value(value)


@step(u"assert '{loc}' value is not '{value}'")
def assert_not_value(context, loc, value):
    QAFWebElement(loc).assert_not_value(value)


@step(u"assert '{loc}' css class name is '{class_name}'")
def assert_css_class(context, loc, class_name):
    QAFWebElement(loc).assert_css_class(class_name)


@step(u"assert '{loc}' css class name is not '{class_name}'")
def assert_not_css_class(context, loc, class_name):
    QAFWebElement(loc).assert_not_css_class(class_name)


@step(u"set '{loc}' attribute '{attr}' value is '{value}'")
def set_attribute(context, loc, attr, value):
    element = QAFWebElement(loc)
    get_driver().execute_script("arguments[0].{attr} = arguments[1]".format(attr=attr), element, value)


@step(u"add cookie '{name}' with value '{value}'")
def add_cookie(context, name, value):
    get_driver().add_cookie({name: value})


@step(u"delete cookie with name '{name}'")
def delete_cookie(context, name):
    get_driver().delete_cookie(name)


@step(u"delete all cookies")
def delete_all_cookies(context):
    get_driver().delete_all_cookies()


@step(u"get a cookie with a name '{name}'")
def get_cookie(context, name):
    get_driver().get_cookie(name)


@step(u"mouse move on '{loc}'")
def mouse_move(context, loc):
    location = QAFWebElement(loc).location
    ActionChains(get_driver()).move_by_offset(location['x'], location['y'])


@step(u"switch to frame '{frame_name}'")
def switch_frame(context, frame_name):
    get_driver().switch_to_frame(frame_name)


@step(u"switch to parent frame")
def switch_to_parent_frame(context):
    get_driver().switch_to_default_content()
