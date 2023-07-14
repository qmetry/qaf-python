import inspect
import re

from qaf.automation.bdd2.qaf_teststep import StepTracker
from qaf.automation.bdd2.step_registry import step_registry
from qaf.automation.core.message_type import MessageType
from qaf.automation.core.qaf_exceptions import StepNotFound
from qaf.automation.core.reporter import Reporter

"""
@author: Chirag Jayswal
"""
pkg_loaded = False


def execute_step(bdd_step_call, testdata=None, is_dryrun_mode: bool = False, should_skip=False):
    if testdata is None:
        testdata = {}
    from qaf.automation.bdd2.model import Bdd2Step
    bdd_step = Bdd2Step(bdd_step_call) if type(bdd_step_call) is str else bdd_step_call
    found, step, args_dict = _find_match(bdd_step.name, testdata)
    if not found:
        Reporter.error(f'{bdd_step.keyword} {bdd_step.name} :Step Not Found'.lstrip())
        if not is_dryrun_mode:
            raise StepNotFound(bdd_step)
    elif should_skip:
        Reporter.log(f'{bdd_step.keyword} {bdd_step.name}'.lstrip(), MessageType.TestStep)
    else:
        execution_tracker = StepTracker(name=bdd_step.name, display_name=f'{bdd_step.keyword} {bdd_step.name}'.lstrip(),
                                        dryrun=is_dryrun_mode, args=[], kwargs=args_dict)
        execution_tracker.call = bdd_step
        bdd_step.stepTracker = execution_tracker
        # if args_dict:
        #     step.executeWithContext(context, **args_dict)
        # else:
        step.execute_with_context(execution_tracker)


def _gen_code_snipet(bdd_step):
    pass


def _convertPrameter(s):
    s = re.sub(r'<(.+?)>', r'${\g<0>}', s)
    return s.replace("${<", "${").replace(">}", "}")


def _find_match(bdd_step_call, testdata):
    from qaf.automation.core.configurations_manager import ConfigurationsManager as CM

    bdd_step_call = _convertPrameter(bdd_step_call)
    bdd_step_call = CM.get_bundle().resolve(bdd_step_call, testdata or {})

    res, match = step_registry.lookup(bdd_step_call)

    if res:
        args_dict = _args_from_match(match)
        return True, res, args_dict

    return False, None, None


def _args_from_match(match):
    args = match.arguments
    argSpec = inspect.getfullargspec(match.func)
    args_dict = {}
    for arg in args:
        args_dict[arg.name] = arg.value.strip("'")

    for var in argSpec.args:
        if var not in args_dict:
            # FullArgSpec(args=['v1', 'v2'], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={'v1': <class 'int'>, 'v2': <class 'str'>})
            # TODO: check for vars to inject, if type specified it will be available in annotations
            # args_dict.update({var: None})
            args_dict[var] = None
    return args_dict


def _get_declaring_class(func):
    try:
        for cls in inspect.getmro(func.im_class):
            if func.__name__ in cls.__dict__:
                return cls
    except:
        pass
    return None
