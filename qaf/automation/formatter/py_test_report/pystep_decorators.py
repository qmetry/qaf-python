from qaf.automation.formatter.py_test_report.meta_info import pytest_component
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus


class pystep(object):

    def __init__(self, keyword="[Func]", name=None):
        self.keyword = keyword
        self.name = name

    def before_step(self, step=None):
        pytest_component.PyTestStep._before_step(name=self.name, keyword=self.keyword, step=step)

    def after_step(self, status, exception=None):
        pytest_component.PyTestStep._after_step(status=status, exception=exception)

    def __call__(self, step):
        def wrapped_step(*args):
            self.before_step(step)
            step(*args)
            self.after_step(status=PyTestStatus.passed.name)

        return wrapped_step
