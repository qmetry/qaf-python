from qaf.automation.formatter.py_test_report.meta_info import pytest_component
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus


class step(object):

    def __init__(self, name=None, keyword="CommonStep:"):
        self.keyword = keyword
        self.name = name

    def before_step(self, step=None):
        pytest_component.PyTestStep._before_step(name=self.name, keyword=self.keyword, step=step)

    def after_step(self, status, exception=None):
        pytest_component.PyTestStep._after_step(status=status, exception=exception)

    def __call__(self, step):
        def wrapped_step(context, *args, **kwargs):
            self.before_step(step)
            step(context, *args, **kwargs)
            self.after_step(status=PyTestStatus.passed.name)

        return wrapped_step