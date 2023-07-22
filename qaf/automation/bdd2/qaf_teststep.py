import re
from dataclasses import dataclass
from inspect import getfullargspec
from typing import Any

from qaf.automation.core.test_base import start_step, end_step, get_test_context
from qaf.automation.keys import SESSION, FIXTURE_NAME, CONTEXT, FIXTURE
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
    metadata: dict
    display_name: str = ""
    dryrun: bool = False
    result: Any = None
    exception = None
    status = PyTestStatus.undefined
    retry: bool = False
    invocation_count: int = 0
    context: Any = None


class QAFTestStep:

    def __init__(self, description="", func: callable = None, keyword: str = "Step", **kwargs):
        if func:
            self.func = func
            self.name = func.__name__
            self.description = description or self.name
        else:
            self.description = description
            self.name = self.description  # inline step
        self.keyword = keyword
        self.metadata = {**kwargs}


    def __enter__(self):  # inline step with Given/When/Then/Step/And(step description):
        # plugin_manager.hook.start_step(uuid=self.uuid, name=self.name, description=self.description)
        start_step(self.name, f'{self.keyword} {self.description}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        # plugin_manager.hook.stop_step(uuid=self.uuid, name=self.name, exc_type=exc_type, exc_val=exc_val,
        #                              exc_tb=exc_tb)
        end_step(True if exc_type is None else False, None)

    def execute(self, *args, **kwargs):
        step_run_context = StepTracker(name=self.name, args=[*args, ], kwargs=kwargs, metadata=self.metadata)
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
            start_step(self.name, step_tracker.display_name, args_array, step_tracker.metadata.get("threshold",0))

    def _formate_name(self, kwargs):
        name = self.description or self.name
        try:
            if kwargs:
                return self.keyword + ' ' + replace_groups(self.matcher.regex_pattern, name, kwargs)
        except BaseException as e:
            pass
        return self.keyword + ' ' + name

    def _prepare_args(self, step_tracker: StepTracker):
        step_tracker.actual_args = list(step_tracker.args)
        step_tracker.actual_kwargs = step_tracker.kwargs.copy()

        step_tracker.kwargs = _getcallargs(self.func, *step_tracker.args, **step_tracker.kwargs)
        step_tracker.args = []
        # step_tracker.kwargs.update({argSpec.args[i]: step_tracker.args.pop(0) for i in range(len(step_tracker.args))})


def _get_val_from_fixture(argname, requestor):
    if hasattr(requestor, SESSION):  # pytest request
        if argname == SESSION:
            return requestor.session
        from _pytest import fixtures
        _request = fixtures.FixtureRequest(requestor, _ispytest=False)
        return _request.getfixturevalue(argname)
    return None


def _getcallargs(func, /, *positional, **named):
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'."""
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = spec
    f_name = func.__name__
    arg2value = {}

    if args[0] == "self" and not positional:
        # if not positional or not  hasattr(positional[0],f_name):
        instance = _get_missing_arg("self", func)
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (instance,) + positional
    num_pos = len(positional)
    num_args = len(args)
    if CONTEXT in args and num_pos + len(named) < num_args:
        pos = args.index(CONTEXT)
        val = _get_missing_arg(CONTEXT, func)
        positional = positional[:pos] + (val,) + positional[pos:]
        num_pos = len(positional)

    num_defaults = len(defaults) if defaults else 0

    n = min(num_pos, num_args)
    for i in range(n):
        arg2value[args[i]] = positional[i]
    if varargs:
        arg2value[varargs] = tuple(positional[n:])
    possible_kwargs = set(args + kwonlyargs)
    if varkw:
        arg2value[varkw] = {}
    for kw, value in named.items():
        if kw not in possible_kwargs:
            if not varkw:
                raise TypeError("%s() got an unexpected keyword argument %r" %
                                (f_name, kw))
            arg2value[varkw][kw] = value
            continue
        if kw in arg2value:
            raise TypeError("%s() got multiple values for argument %r" %
                            (f_name, kw))
        arg2value[kw] = value
    # if num_pos > num_args and not varargs:
    # do nothing let actual call fail with to many argument error
    if num_pos < num_args:
        req = args[:num_args - num_defaults]
        for arg in req:
            if arg not in arg2value:
                arg2value[arg] = _get_missing_arg(arg, func)
        for i, arg in enumerate(args[num_args - num_defaults:]):
            if arg not in arg2value:
                arg2value[arg] = _get_missing_arg(arg, func) \
                    if defaults[i] == FIXTURE \
                    else defaults[i]
    for kwarg in kwonlyargs:
        if kwarg not in arg2value:
            if kwonlydefaults and kwarg in kwonlydefaults:
                arg2value[kwarg] = kwonlydefaults[kwarg]
            else:
                arg2value[kwarg] = _get_missing_arg(kwarg, func)

    return arg2value


def _get_missing_arg(argname, func):
    if "self" == argname:
        cls_qualname = get_func_declaring_class(func)
        cls = get_class(cls_qualname)
        if cls is None:
            instance = None
        if hasattr(cls, FIXTURE_NAME) and cls.fixture_name:
            instance = _get_val_from_fixture(getattr(cls, FIXTURE_NAME), get_test_context())
        else:
            instance = cls()
        return instance
    if CONTEXT == argname:
        return get_test_context()

    return _get_val_from_fixture(argname, get_test_context())
