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

from http.client import responses

import jmespath
from hamcrest import *

from qaf.automation.bdd2.step_registry import step
from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.util.validator import Validator
from qaf.automation.ws.rest.ws_request import WsRequest
from qaf.automation.ws.ws_request_bean import WsRequestBean


@step(u"user requests '{api_key}' with data '{data}'")
def user_requests_with_data(context, api_key, data):
    ws_request_bean = WsRequestBean().fill_from_config(api_key)
    WsRequest().request(ws_request_bean, data)


@step(u"user requests '{api_key}'")
def user_requests(context, api_key):
    ws_request_bean = WsRequestBean().fill_from_config(api_key)
    WsRequest().request(ws_request_bean)


############################
# Status Code Verification #
############################

@step(u"response should have status code '{status_code}'")
def response_should_have_status_code(context, status_code):
    Validator.assert_that(WsRequest.response.status_code, equal_to(int(status_code)), reason="Response Status")


@step(u"response should have status '{status}'")
def response_should_have_status(context, status):
    Validator.assert_that(responses[WsRequest.response.status_code], equal_to(status), reason="Response Status")


#######################
# Header Verification #
#######################

@step(u"response should have header '{header}' with value '{value}'")
def verify_should_have_header_with_value(context, header, value):
    Validator.assert_that(WsRequest.response.headers, has_entry(key_match=header, value_match=value),
                          reason="Response Header")


@step(u"response should have header '{header}'")
def verify_should_have_header(context, header):
    Validator.assert_that(WsRequest.response.headers, has_key(header), reason="Response Header")


@step(u"store response header '{header}' into '{variable}'")
def store_response_body_to(context, header, variable):
    CM().set_object_for_key(variable, str(WsRequest.response.headers[header]))


#####################
# Body Verification #
#####################

@step(u"store response body '{path}' into '{variable}'")
def store_response_body_to(context, path, variable):
    value = value_at_json_path(WsRequest.response.json(), path)
    CM().set_object_for_key(variable, str(value))


@step(u"response should have '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to(value))


@step(u"response should have '{path}'")
def response_should_have_jsonpath(context, path):
    Validator.assert_that(has_json_path(WsRequest.response.json(), path), equal_to(True),
                          reason="Response Body has " + path)


@step(u"response should not have '{path}'")
def response_should_have_jsonpath(context, path):
    Validator.assert_that(has_json_path(WsRequest.response.json(), path), equal_to(False),
                          reason="Response Body has " + path)


@step(u"response should have value contains '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), contains_string(value))


@step(u"response should have value ignoring case '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to_ignoring_case(value))


@step(u"response should have value ignoring whitespace '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to_ignoring_whitespace(value))


@step(u"response should have value contains ignoring case '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value).upper(), contains_string(value.upper()))


@step(u"response should have value end with '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), ends_with(value))


@step(u"response should have value start with '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), starts_with(value))


@step(u"response should have value matches with '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), matches_regexp(value))


@step(u"response should start with '{value}' at '{path}'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), starts_with(value))


@step(u"response should be less than '{value}' at '{path}'")
def response_should_less_than(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), less_than(value))


@step(u"response should be less than or equals to '{value}' at '{path}'")
def response_should_less_than_or_equals_to(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), less_than_or_equal_to(value))


@step(u"response should be greater than '{value}' at '{path}'")
def response_should_greater_than(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), greater_than(value))


@step(u"response should be greater than or equals to '{value}' at '{path}'")
def response_should_greater_than_or_equals_to(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), greater_than_or_equal_to(value))


@step(u"download file as '{file_name}' from '{response}'")
def download_file_from_response(context, file_name, response):
    raise NotImplemented


def has_json_path(json, path):
    expression = jmespath.compile(path)
    value = expression.search(json)
    return False if value is None else True


def value_at_json_path(json, path):
    expression = jmespath.compile(path)
    return expression.search(json)
