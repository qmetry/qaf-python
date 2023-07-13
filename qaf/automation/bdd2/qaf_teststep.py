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

    def executeWithContext(self, step_tracker: StepTracker):
        step_tracker.step = self
        while step_tracker.invocation_count == 0 or step_tracker.retry:
            step_tracker.invocation_count += 1
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
                try:
                    if step_tracker.args or step_tracker.kwargs:
                        # step_run_context.step.args = [*args, ]
                        step_tracker.display_name = self._formate_name(step_tracker.args, step_tracker.kwargs)
                    else:
                        step_tracker.display_name = self.description or self.name
                except Exception as e:
                    step_tracker.display_name = self.name
            args_array = [step_tracker.actual_args]
            if step_tracker.actual_kwargs:
                for key, value in step_tracker.actual_kwargs.items():
                    args_array.append(str(key) + ':' + str(value))
            start_step(self.name, step_tracker.display_name, args_array)

    def _formate_name(self, args, kwargs):
        name = self.description or self.name
        try:
            if args:
                name = re.sub(r'\((.*?)\)', lambda match: str(args.pop(0)), self.matcher.regex_pattern)
            if kwargs:
                #name = self.description.format(**kwargs)
                name = replace_groups(self.matcher.regex_pattern, name, **kwargs)
        except:
            pass
        return self.keyword + ' ' + name

    def _prepare_args(self, step_tracker: StepTracker):
        argSpec = inspect.getfullargspec(self.func)
        step_tracker.actual_args = list(step_tracker.args)
        step_tracker.actual_kwargs = step_tracker.kwargs.copy()

        if len(step_tracker.args) + len(step_tracker.kwargs) != len(argSpec.args):
            if step_tracker.args:
                if "context" == argSpec.args[0] \
                        and type(step_tracker.args[0]) != type(step_tracker.context):
                    step_tracker.args = [step_tracker.context]
                    step_tracker.args.extend(step_tracker.actual_args)
                step_tracker.kwargs.update({argSpec.args[i]: step_tracker.args.pop(0)
                                            for i in range(len(step_tracker.args))})

            argset = set(argSpec.args) - set(step_tracker.kwargs)
            for argname in argset:  # check available pytest fixture to inject
                if "context" == argname:
                    step_tracker.kwargs[argname] = step_tracker.context
                if hasattr(step_tracker.context, "session"):  # pytest request
                    fm = step_tracker.context.session._fixturemanager
                    fdefs = fm.getfixturedefs(argname=argname, nodeid=step_tracker.context.node.nodeid)
                    if fdefs:
                        for fdef in fdefs:
                            step_tracker.kwargs[argname] = step_tracker.context.node.ihook.pytest_fixture_setup(
                                fixturedef=fdef,
                                request=step_tracker.context)
                            break


def replace_groups(pattern, string, replacements):
    pattern = re.compile(pattern)
    # create a dict of {group_index: group_name} for use later
    groupnames = {index: name for name, index in pattern.groupindex.items()}

    def repl(match):
        # we have to split the matched text into chunks we want to keep and
        # chunks we want to replace
        # captured text will be replaced. uncaptured text will be kept.
        text = match.group()
        chunks = []
        lastindex = 0
        for i in range(1, pattern.groups + 1):
            groupname = groupnames.get(i)
            if groupname not in replacements:
                continue

            # keep the text between this match and the last
            chunks.append(text[lastindex:match.start(i)])
            # then instead of the captured text, insert the replacement text for this group
            chunks.append(replacements[groupname])
            lastindex = match.end(i)
        chunks.append(text[lastindex:])
        # join all the junks to obtain the final string with replacements
        return ''.join(chunks)

    # for each occurence call our custom replacement function
    return re.sub(pattern, repl, string)
