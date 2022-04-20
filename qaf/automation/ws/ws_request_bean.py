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

import json

from requests.hooks import default_hooks
from requests.utils import default_headers

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.util.string_util import is_not_blank


class WsRequestBean:

    def __init__(self):
        self.__baseUrl = ""
        self.__endPoint = ""
        self.__to_string = {}

        self.__method = "GET"  # POST, PUT, DELETE, HEAD, PATCH, and OPTIONS.
        self.__params = None  # {'q': 'keyword'} or [{'q': 'keyword'}]
        self.__data = None  # {'key':'value'}
        self.__headers = default_headers()  # {'Accept': 'application/vnd.github.v3.text-match+json'}
        self.__cookies = None  # {'key':'value'}
        self.__files = None  # {'upload_file': open('file.txt','rb')}
        self.__auth = None  # ('username', 'password') in a tuple
        self.__timeout = 60  # 1 or (1, 2) in tuple
        self.__allow_redirects = True  # Boolean
        self.__proxies = None  # {"http": "http://10.10.10.10:8000", "https": "http://10.10.10.10:8000"}
        self.__hooks = default_hooks()
        self.__stream = None  # Boolean
        self.__verify = None  # Boolean
        self.__cert = None  # ('/path/server.crt', '/path/key')
        self.__json = None  # {'key':'value'}

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, value):
        self.__method = value.upper()

    @property
    def url(self):
        url = self.baseUrl
        if is_not_blank(self.__endPoint):
            url = url + self.__endPoint
        return url

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self, value):
        self.__params = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        self.__headers = value

    @property
    def cookies(self):
        return self.__cookies

    @cookies.setter
    def cookies(self, value):
        self.__cookies = value

    @property
    def files(self):
        return self.__files

    @files.setter
    def files(self, value):
        self.__files = value
        if value is not None:
            updated_files = {}
            for key, val in value.items():
                updated_files[key] = open(val, 'rb')
            self.__files = updated_files

    @property
    def auth(self):
        return self.__auth

    @auth.setter
    def auth(self, value):
        self.__auth = value

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        self.__timeout = value

    @property
    def allow_redirects(self):
        return self.__allow_redirects

    @allow_redirects.setter
    def allow_redirects(self, value):
        self.__allow_redirects = value

    @property
    def proxies(self):
        return self.__proxies

    @proxies.setter
    def proxies(self, value):
        self.__proxies = value

    @property
    def hooks(self):
        return self.__hooks

    @hooks.setter
    def hooks(self, value):
        self.__hooks = value

    @property
    def stream(self):
        return self.__stream

    @stream.setter
    def stream(self, value):
        self.__stream = value

    @property
    def verify(self):
        return self.__verify

    @verify.setter
    def verify(self, value):
        self.__verify = value

    @property
    def cert(self):
        return self.__cert

    @cert.setter
    def cert(self, value):
        self.__cert = value

    @property
    def json(self):
        return self.__json

    @json.setter
    def json(self, value):
        self.__json = value

    @property
    def baseUrl(self):
        return self.__baseUrl if is_not_blank(self.__baseUrl) else CM().get_str_for_key(
            AP.SELENIUM_BASE_URL)

    @baseUrl.setter
    def baseUrl(self, value):
        self.__baseUrl = value

    @property
    def endPoint(self):
        return self.__endPoint

    @endPoint.setter
    def endPoint(self, value):
        self.__endPoint = value

    @property
    def to_string(self):
        return self.__to_string

    @to_string.setter
    def to_string(self, value):
        self.__to_string = value

    def fill_from_config(self, key):
        _value = CM().get_object_for_key(key, key)
        _dict = json.loads(_value)
        self.fill_data(_dict)
        return self

    def resolve_parameters(self, data):
        _dict = json.loads(data)
        self.fill_data(_dict)

    def fill_data(self, dict):
        if "reference" in dict:
            self.fill_from_config(dict["reference"])

        self.to_string = dict

        for key, value in dict.items():
            if hasattr(self, key):
                object.__setattr__(self, key, value)