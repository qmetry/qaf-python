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

import requests
from requests import PreparedRequest

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.load_class import load_class
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver.command_tracker import CommandTracker
from qaf.automation.ws.rest.ws_listener import WsListener
from qaf.automation.ws.ws_request_bean import WsRequestBean


class WsRequest:
    response = None

    def __init__(self) -> None:
        self.__listeners = []
        self.__listeners.append(WsListener())

        if CM().contains_key(AP.WEBSERVICE_COMMAND_LISTENERS):
            class_name = CM().get_str_for_key(AP.WEBSERVICE_COMMAND_LISTENERS)
            self.__listeners.append(load_class(class_name)())

    def request(self, request_bean: WsRequestBean) -> dict:
        command_tracker = CommandTracker(request_bean.endPoint, request_bean.to_string)
        s, prep, send_kwargs = self.prepare_request(request_bean)
        self.before_command(command_tracker)

        try:
            WsRequest.response = s.send(prep, **send_kwargs)
            command_tracker.response = WsRequest.response

        except Exception as e:
            self.on_exception(command_tracker)
            command_tracker.exception = e

        if command_tracker.has_exception():
            if command_tracker.retry:
                WsRequest.response = s.send(prep, **send_kwargs)
                command_tracker.response = WsRequest.response
                command_tracker.exception = None
            else:
                raise command_tracker.exception
        self.after_command(command_tracker)
        return command_tracker.response

    def prepare_request(self, request_bean: WsRequestBean) -> (requests.Session, PreparedRequest, dict):
        s = requests.Session()

        req = requests.Request(
            method=request_bean.method.upper(),
            url=request_bean.url,
            headers=request_bean.headers,
            files=request_bean.files,
            data=request_bean.data or {},
            json=request_bean.json,
            params=request_bean.params or {},
            auth=request_bean.auth,
            cookies=request_bean.cookies,
            hooks=request_bean.hooks,
        )

        prep = s.prepare_request(req)

        proxies = request_bean.proxies or {}

        settings = s.merge_environment_settings(
            prep.url, proxies, request_bean.stream, request_bean.verify, request_bean.cert
        )

        send_kwargs = {
            'timeout': request_bean.timeout,
            'allow_redirects': request_bean.allow_redirects,
        }
        send_kwargs.update(settings)
        return s, prep, send_kwargs

    def before_command(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.before_command(self, command_tracker)

    def after_command(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.after_command(self, command_tracker)

    def on_exception(self, command_tracker: CommandTracker) -> None:
        if self.__listeners is not None:
            for listener in self.__listeners:
                listener.on_exception(self, command_tracker)
