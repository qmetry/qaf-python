import inspect
import re
from dataclasses import dataclass
from typing import Any

from qaf.automation.core.test_base import start_step, end_step, get_test_context
from qaf.automation.report.utils import step_status
from qaf.listeners import pluginmagager
from qaf.pytest.pytest_utils import PyTestStatus


@dataclass
class StepTracker:
    args: list[Any]
    kwargs: dict
    name: str
    display_name: str = ""
    dryrun: bool = False
    result: Any = None
    exception = None
    status = PyTestStatus.undefined
    retry: bool = False
    invocation_count: int = 0
    context: Any = None


class QAFTestStep:

    def __init__(self, description="", func: callable = None, keyword: str = "Step"):
        if func:
            self.func = func
            self.name = func.__name__
            self.description = description or self.name
        else:
            self.description = description
            self.name = self.description  # inline step
        self.keyword = keyword

    def __enter__(self):  # inline step with Given/When/Then/Step/And(step description):
        # plugin_manager.hook.start_step(uuid=self.uuid, name=self.name, description=self.description)
        start_step(self.name, f'{self.keyword} {self.description}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        # plugin_manager.hook.stop_step(uuid=self.uuid, name=self.name, exc_type=exc_type, exc_val=exc_val,
        #                              exc_tb=exc_tb)
        end_step(True if exc_type is None else False, None)

    def execute(self, *args, **kwargs):
        step_run_context = StepTracker(name=self.name, args=args, kwargs=kwargs)
        return self.executeWithContext(step_run_context)

    def executeWithContext(self, step_run_context: StepTracker):
        step_run_context.step = self
        while step_run_context.invocation_count == 0 or step_run_context.retry:
            step_run_context.invocation_count += 1
            self.before_step(step_run_context)
            step_run_context.status = PyTestStatus.executing
            step_run_context.retry = False # reset
            try:
                if not step_run_context.dryrun:
                    res = self.func(*step_run_context.args, **step_run_context.kwargs)
                    step_run_context.result = res
                step_run_context.status = PyTestStatus.passed
                self.after_step(step_run_context)
                return step_run_context.result
            except Exception as e:
                step_run_context.exception = e
                step_run_context.status = PyTestStatus.failed
                self.after_step(step_run_context)

        if step_run_context.exception:
            raise step_run_context.exception

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

    def after_step(self, step_tracker: StepTracker):
        pluginmagager.hook.after_step(step_tracker=step_tracker)
        if not step_tracker.retry:
            status_text = step_status(step_tracker)
            b_status = bool(re.search('(?i)pass', status_text)) if bool(re.search('(?i)fail|pass', status_text)) else None
            end_step(b_status, step_tracker.result)

    def before_step(self, step_tracker: StepTracker):
        step_tracker.context = get_test_context()
        pluginmagager.hook.before_step(step_tracker=step_tracker)
        if not step_tracker.display_name:
            try:
                if step_tracker.args or step_tracker.kwargs:
                    # step_run_context.step.args = [*args, ]
                    step_tracker.display_name = self._formate_name(step_tracker.args, step_tracker.kwargs)
                else:
                    step_tracker.display_name = self.name
            except Exception as e:
                step_tracker.display_name = self.name

        if step_tracker.invocation_count == 1:
            args_array = [step_tracker.args]
            if step_tracker.kwargs:
                for key, value in step_tracker.kwargs.items():
                    args_array.append(str(key) + ':' + str(value))
            start_step(self.name, step_tracker.display_name, args_array)
            self._prepare_args(step_tracker)


    def _formate_name(self, *args, **kwargs):
        name = self.description or self.name
        if args:
            name = re.sub("", lambda match: str(args.pop(0)), self.matcher.regex_pattern)
        if kwargs:
            name = self.description.format(kwargs)
            name = re.sub(self.pattern, lambda match: str(kwargs[match.group()]), name)
        return self.keyword + ' ' + name

    def _prepare_args(self, step_tracker:StepTracker):
        argSpec = inspect.getfullargspec(self.func)
        step_tracker.actual_args = list(step_tracker.args)
        if step_tracker.args and len(step_tracker.args) != len(argSpec.args):
            if "context" in argSpec.args and not(step_tracker.kwargs and "context" in  step_tracker.kwargs):
                step_tracker.args = [step_tracker.context]
                step_tracker.args.extend(step_tracker.actual_args)
        elif "context" in argSpec.args and not(step_tracker.kwargs and "context" in  step_tracker.kwargs):
            step_tracker.kwargs["context"] = step_tracker.context


