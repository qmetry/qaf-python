import inspect
import re
from dataclasses import dataclass
from typing import Any

from qaf.automation.core.test_base import start_step, end_step, get_test_context
from qaf.automation.report.utils import step_status
from qaf.automation.util.class_util import get_func_declaring_class, get_class
from qaf.automation.util.string_util import replace_groups
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
        step_run_context = StepTracker(name=self.name, args=[*args, ], kwargs=kwargs)
        return self.execute_with_context(step_run_context)

    def execute_with_context(self, step_tracker: StepTracker):
        step_tracker.step = self
        while step_tracker.invocation_count == 0 or step_tracker.retry:
            step_tracker.invocation_count += 1
            step_tracker.description = self.description
            self.before_step(step_tracker)
            step_tracker.status = PyTestStatus.executing
            step_tracker.retry = False  # reset
            try:
                if not step_tracker.dryrun:
                    res = self.func(*step_tracker.args, **step_tracker.kwargs)
                    step_tracker.result = res
                step_tracker.status = PyTestStatus.passed
                self.after_step(step_tracker)
                return step_tracker.result
            except Exception as e:
                step_tracker.exception = e
                step_tracker.status = PyTestStatus.failed
                self.after_step(step_tracker)

        if step_tracker.exception:
            raise step_tracker.exception

    def __call__(self, *args, **kwargs):
        if args and callable(args[0]):
            self._decorate(args[0])
            return self
        return self.execute(*args, **kwargs)

    def __get__(self, instance, owner):
        from functools import partial
        return partial(self.__call__, instance)

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
            b_status = bool(re.search('(?i)pass', status_text)) if bool(
                re.search('(?i)fail|pass', status_text)) else None
            end_step(b_status, step_tracker.result)

    def before_step(self, step_tracker: StepTracker):
        step_tracker.context = get_test_context()
        pluginmagager.hook.before_step(step_tracker=step_tracker)

        if step_tracker.invocation_count == 1:
            self._prepare_args(step_tracker)
            if not step_tracker.display_name:
                step_tracker.display_name = self._formate_name(step_tracker.kwargs)
            args_array = [step_tracker.actual_args]
            if step_tracker.actual_kwargs:
                for key, value in step_tracker.actual_kwargs.items():
                    args_array.append(str(key) + ':' + str(value))
            start_step(self.name, step_tracker.display_name, args_array)

    def _formate_name(self, kwargs):
        name = self.description or self.name
        try:
            if kwargs:
                return self.keyword + ' ' + replace_groups(self.matcher.regex_pattern, name, kwargs)
        except BaseException as e:
            pass
        return self.keyword + ' ' + name

    def _prepare_args(self, step_tracker: StepTracker):
        argSpec = inspect.getfullargspec(self.func)
        step_tracker.actual_args = list(step_tracker.args)
        step_tracker.actual_kwargs = step_tracker.kwargs.copy()

        if len(step_tracker.args) + len(step_tracker.kwargs) != len(argSpec.args):
            if step_tracker.args:
                context_pos = argSpec.args.index("context") \
                    if "context" in argSpec.args and "context" not in step_tracker.kwargs else -1
                if 0 <= context_pos < len(step_tracker.args):
                    step_tracker.args = []
                    step_tracker.args.extend(step_tracker.actual_args)
                    step_tracker.args.insert(context_pos, step_tracker.context or step_tracker)
        step_tracker.kwargs.update({argSpec.args[i]: step_tracker.args.pop(0) for i in range(len(step_tracker.args))})

        argset = set(argSpec.args) - set(step_tracker.kwargs)
        for argname in argset:  # check available pytest fixture to inject
            if "self" == argname:
                cls_qualname = get_func_declaring_class(self.func)
                cls = get_class(cls_qualname)
                if cls is None:
                    instance = None
                if hasattr(cls, "fixture_name") and cls.fixture_name:
                    instance = _get_val_from_fixture(getattr(cls, "fixture_name"),step_tracker.context)
                else:
                    instance = cls()
                step_tracker.kwargs[argname] = instance
                continue
            if "context" == argname:
                step_tracker.kwargs[argname] = step_tracker.context or step_tracker
                continue
            step_tracker.kwargs[argname] = _get_val_from_fixture(argname, step_tracker.context)


def _get_val_from_fixture(argname, requestor):
    if hasattr(requestor, "session"):  # pytest request
        from _pytest import fixtures
        _request = fixtures.FixtureRequest(requestor, _ispytest=False)
        return _request.getfixturevalue(argname)
    return None
