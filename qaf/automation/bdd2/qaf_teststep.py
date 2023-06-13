import re
from dataclasses import dataclass
from typing import Any

from qaf.automation.core.test_base import start_step, end_step
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus
from qaf.automation.report.utils import step_status


@dataclass
class StepRunContext:
    args: list[Any]
    kwargs: dict

    def __init__(self, display_name="", dryrun=False):
        self.display_name = display_name
        self.status = PyTestStatus.undefined
        self.result = None
        self.exception = None
        self.dryrun = dryrun


class QAFTestStep:

    def __init__(self, description="", func: callable = None):
        if func:
            self.func = func
            self.name = func.__name__
            self.description = description or self.name
        else:
            self.description = description

    def execute(self, *args, **kwargs):
        step_run_context = StepRunContext()
        return self.executeWithContext(step_run_context, *args, **kwargs)

    def executeWithContext(self, step_run_context: StepRunContext, *args, **kwargs):
        step_run_context.step = self
        self.before_step(step_run_context, *args, **kwargs)
        try:
            if not step_run_context.dryrun:
                res = self.func(*args, **kwargs)
                step_run_context.result = res
            step_run_context.status = PyTestStatus.passed
            self.after_step(step_run_context)
            return step_run_context.result
        except Exception as e:
            step_run_context.exception = e
            step_run_context.status = PyTestStatus.failed
            self.after_step( step_run_context)
            raise e

    def __call__(self, *args, **kwargs):
        if args and callable(args[0]):
            self._decorate(args[0])
            return self
        self.execute(*args, **kwargs)

    def _decorate(self, func):
        from qaf.automation.bdd2.step_registry import step_registry
        self.func = func
        self.func.wrapper = self
        self.name = func.__name__
        self.description = self.description or self.name
        step_registry.register_step(self)

    def after_step(self, step_run_context: StepRunContext):
        status_text = step_status(step_run_context)
        b_status = bool(re.search('(?i)pass', status_text)) if bool(re.search('(?i)fail|pass', status_text)) else None
        end_step(b_status, step_run_context.result)

    def before_step(self, step_run_context: StepRunContext, *args, **kwargs):
        if not step_run_context.display_name:
            try:
                if args or kwargs:
                    # step_run_context.step.args = [*args, ]
                    step_run_context.display_name = self._formate_name(args, kwargs)
                    step_run_context.args = args
                    step_run_context.kwargs = kwargs
                else:
                    step_run_context.display_name = self.name
            except Exception as e:
                step_run_context.display_name = self.name
        args_array = [*args]
        if kwargs:
            for key, value in kwargs.items():
                args_array.append(str(key) + ':' + str(value))
        start_step(self.name, step_run_context.display_name, args_array)
        step_run_context.status = PyTestStatus.executing

    def _formate_name(self, *args, **kwargs):
        name = self.name
        if args:
            name = re.sub(self.pattern, lambda match: str(args.pop(0)), name)
        if kwargs:
            name = re.sub(self.pattern, lambda match: str(kwargs[match.group()]), name)
        return self.keyword + ' ' + name
