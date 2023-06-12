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
import inspect
import re

from qaf.automation.core.test_base import start_step, end_step
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus
from qaf.automation.formatter.qaf_report.util.utils import step_status

steps_mapping = {}


class step(object):

    def __init__(self, name=None, keyword=""):
        self.args = []
        self.exception = None
        self.keyword = keyword
        self.name = name
        self.status = PyTestStatus.undefined
        self.pattern = r'\((.*?)\)'

    def before_step(self, func, *args, **kwargs):
        try:
            if args or kwargs:
                self.args = [*args, ]
                display_name = self._formate_name(args, kwargs)
                # self.keyword + ' ' + re.sub(r'\((.*?)\)', lambda match: str(self.args.pop(0)), self.name)
                self.args = [*args, ]
            else:
                display_name = self.keyword + ' ' + self.name
        except Exception as e:
            display_name = self.keyword + ' ' + self.name
        start_step(func.__name__, display_name, [*args, ])

    def after_step(self, status, result):
        self.status = status
        status_text = step_status(self)
        b_status = bool(re.search('(?i)pass', status_text)) if bool(re.search('(?i)fail|pass', status_text)) else None
        end_step(b_status, result)

    def __call__(self, func):
        def wrapped_step(*args, **kwargs):
            self.before_step(func, *args, **kwargs)
            try:
                res = func(*args, **kwargs)
                self.after_step(status=PyTestStatus.passed, result=res)
                return res
            except Exception as e:
                self.exception = e
                self.after_step(status=PyTestStatus.failed, result=None)
                raise e

        module = func.__module__  # sys.modules[func.__module__]
        wrapped_step.__module__ = func.__module__
        wrapped_step.argSpec = inspect.getfullargspec(func)
        steps_mapping[self.name] = wrapped_step
        return wrapped_step

    def _formate_name(self, *args, **kwargs):
        name = self.name

        if args:
            name = re.sub(self.pattern, lambda match: str(args.pop(0)), name)
        if kwargs:
            name = re.sub(self.pattern, lambda match: str(kwargs[match.group()]), name)
        return self.keyword + ' ' + name
