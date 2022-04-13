from behave import *
from hamcrest import *

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.util.validator import Validator
from qaf.automation.ws.rest.ws_request import WsRequest
from qaf.automation.ws.ws_request_bean import WsRequestBean
from http.client import responses
import jmespath

use_step_matcher("re")


@step(u"user requests '(?P<api_key>[\S\s]+)' with data '(?P<data>[\S\s]+)'")
def user_requests_with_data(context, api_key, data):
    ws_request_bean = WsRequestBean().fill_from_config(api_key)
    ws_request_bean.resolve_parameters(data)
    WsRequest().request(ws_request_bean)


@step(u"user requests '(?P<api_key>[\S\s]+)'")
def user_requests(context, api_key):
    WsRequest().request(WsRequestBean().fill_from_config(api_key))


############################
# Status Code Verification #
############################

@step(u"response should have status code '(?P<status_code>[\S\s]+)'")
def response_should_have_status_code(context, status_code):
    Validator.assert_that(WsRequest.response.status_code, equal_to(int(status_code)), reason="Response Status")


@step(u"response should have status '(?P<status>[\S\s]+)'")
def response_should_have_status(context, status):
    Validator.assert_that(responses[WsRequest.response.status_code], equal_to(status), reason="Response Status")


#######################
# Header Verification #
#######################

@step(u"response should have header '(?P<header>[\S\s]+)' with value '(?P<value>[\S\s]+)'")
def verify_should_have_header_with_value(context, header, value):
    Validator.assert_that(WsRequest.response.headers, has_entry(key_match=header, value_match=value),
                          reason="Response Header")


@step(u"response should have header '(?P<header>[\S\s]+)'")
def verify_should_have_header(context, header):
    Validator.assert_that(WsRequest.response.headers, has_key(header), reason="Response Header")


@step(u"store response header '(?P<header>[\S\s]+)' into '(?P<variable>[\S\s]+)'")
def store_response_body_to(context, header, variable):
    CM().set_object_for_key(variable, str(WsRequest.response.headers[header]))


#####################
# Body Verification #
#####################

@step(u"store response body '(?P<path>[\S\s]+)' into '(?P<variable>[\S\s]+)'")
def store_response_body_to(context, path, variable):
    value = value_at_json_path(WsRequest.response.json(), path)
    CM().set_object_for_key(variable, str(value))


@step(u"response should have '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to(value))


@step(u"response should have '(?P<path>[\S\s]+)'")
def response_should_have_jsonpath(context, path):
    Validator.assert_that(has_json_path(WsRequest.response.json(), path), equal_to(True),
                          reason="Response Body has " + path)


@step(u"response should not have '(?P<path>[\S\s]+)'")
def response_should_have_jsonpath(context, path):
    Validator.assert_that(has_json_path(WsRequest.response.json(), path), equal_to(False),
                          reason="Response Body has " + path)


@step(u"response should have value contains '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), contains_string(value))


@step(u"response should have value ignoring case '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to_ignoring_case(value))


@step(u"response should have value ignoring whitespace '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), equal_to_ignoring_whitespace(value))


@step(u"response should have value contains ignoring case '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value).upper(), contains_string(value.upper()))


@step(u"response should have value end with '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), ends_with(value))


@step(u"response should have value start with '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), starts_with(value))


@step(u"response should have value matches with '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), matches_regexp(value))


@step(u"response should start with '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_have_value_at_jsonpath(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(str(actual_value), starts_with(value))


@step(u"response should be less than '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_less_than(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), less_than(value))


@step(u"response should be less than or equals to '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_less_than_or_equals_to(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), less_than_or_equal_to(value))


@step(u"response should be greater than '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_greater_than(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), greater_than(value))


@step(u"response should be greater than or equals to '(?P<value>[\S\s]+)' at '(?P<path>[\S\s]+)'")
def response_should_greater_than_or_equals_to(context, value, path):
    actual_value = value_at_json_path(WsRequest.response.json(), path)
    Validator.assert_that(int(actual_value), greater_than_or_equal_to(value))


@step(u"download file as '(?P<file_name>[\S\s]+)' from '(?P<response>[\S\s]+)'")
def download_file_from_response(context, file_name, response):
    raise NotImplemented


def has_json_path(json, path):
    expression = jmespath.compile(path)
    value = expression.search(json)
    return False if value is None else True


def value_at_json_path(json, path):
    expression = jmespath.compile(path)
    return expression.search(json)
