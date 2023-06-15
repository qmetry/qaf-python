import inspect
import os
import re

from qaf.automation.bdd2.qaf_teststep import StepRunContext
from qaf.automation.bdd2.step_registry import step_registry
from qaf.automation.core.reporter import Reporter

"""
@author: Chirag Jayswal
"""
pkg_loaded = False


def execute_step(bdd_step, testdata={}, is_dryrun_mode: bool = False):
    bdd_step_call = bdd_step if type(bdd_step) is str else bdd_step.name
    found, step, args_dict = _find_match(bdd_step_call, testdata)
    if not found:
        Reporter.error("{}  Step Not Found".format(bdd_step_call))
        if not is_dryrun_mode:
            raise Exception("Step Implementation Not Found")
    else:
        context = StepRunContext(bdd_step_call, is_dryrun_mode)
        if args_dict:
            step.executeWithContext(context, **args_dict)
        else:
            step.executeWithContext(context)


def _gen_code_snnipet(bdd_step):
    pass


def _convertPrameter(s):
    s = re.sub(r'<[a-z0-9-_]+>', r'${\g<0>}', s)
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


def _find_match_old(bdd_step_call, testdata):
    from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
    steps_mapping = step_registry.registry
    bdd_step_call = _convertPrameter(bdd_step_call)
    bdd_step_call = CM.get_bundle().resolve(bdd_step_call, testdata or {})
    for expr in steps_mapping:
        # Reporter.log([step_call, expr])
        if re.search(expr, bdd_step_call):
            args_dict = re.match(expr, bdd_step_call).groupdict()
            step_fun = steps_mapping[expr]
            argSpec = step_fun.argSpec
            module = step_fun.__module__
            # declaring_class = _get_declaring_class(func)
            for var in argSpec.args:
                if var not in args_dict:
                    # FullArgSpec(args=['v1', 'v2'], varargs=None, varkw=None, defaults=None, kwonlyargs=[], kwonlydefaults=None, annotations={'v1': <class 'int'>, 'v2': <class 'str'>})
                    # TODO: check for vars to inject, if type specified it will be available in annotations
                    args_dict.update({var: None})
            return True, step_fun, args_dict
    return False, None, None


def _get_declaring_class(func):
    try:
        for cls in inspect.getmro(func.im_class):
            if func.__name__ in cls.__dict__:
                return cls
    except:
        pass
    return None


def load_step_modules(step_paths):
    """Load step modules with step definitions from step_paths directories."""
    from behave import matchers
    from qaf.automation.bdd2.step_registry import setup_step_decorators
    from behave.runner_util import PathManager, exec_file

    step_globals = {
        "use_step_matcher": matchers.use_step_matcher,
    }
    setup_step_decorators(step_globals)

    # -- Allow steps to import other stuff from the steps dir
    # NOTE: Default matcher can be overridden in "environment.py" hook.
    with PathManager(step_paths):
        default_matcher = matchers.current_matcher
        for path in step_paths:
            for name in sorted(os.listdir(path)):
                if name.endswith(".py"):
                    # -- LOAD STEP DEFINITION:
                    # Reset to default matcher after each step-definition.
                    # A step-definition may change the matcher 0..N times.
                    # ENSURE: Each step definition has clean globals.
                    # try:
                    step_module_globals = step_globals.copy()
                    exec_file(os.path.join(path, name), step_module_globals)
                    matchers.current_matcher = default_matcher
