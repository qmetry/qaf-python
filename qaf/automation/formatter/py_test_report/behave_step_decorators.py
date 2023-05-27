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
import re

from qaf.automation.formatter.py_test_report.meta_info import pytest_component
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus


class step(object):

    def __init__(self, name=None, keyword=""):
        self.args = []
        self.exception = None
        self.keyword = keyword
        self.name = name
        self.status = PyTestStatus.undefined.name

    def before_step(self, step=None, *args, **kwargs):
        try:
            if args:
                self.args = [*args, ]
                self.name = re.sub(r'\((.*?)\)', lambda match: str(self.args.pop(0)), self.name)
        except:
            pass
        pytest_component.PyTestStep._before_step(self.name, self.keyword, step, *args)

    def after_step(self, status, exception=None):
        pytest_component.PyTestStep._after_step(status=status, exception=exception)

    def __call__(self, step):
        def wrapped_step(context, *args, **kwargs):
            self.before_step(step, *args, **kwargs)
            try:
                step(context, *args, **kwargs)
                self.after_step(status=PyTestStatus.passed.name)
            except Exception as e:
                self.after_step(status=PyTestStatus.failed.name, exception=e)
                raise e

        return wrapped_step
