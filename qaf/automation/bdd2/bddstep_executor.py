import inspect
import re

from qaf.automation.core.message_type import MessageType
from qaf.automation.core.reporter import Reporter
from qaf.automation.formatter.py_test_report.qafstep_decorator import steps_mapping

"""
@author: Chirag Jayswal
"""
pkg_loaded = False


def load_pkgs():
    pass


def execute_step(bdd_step, testdata, is_dryrun_mode: bool = False):
    if not pkg_loaded:
        load_pkgs()
    bdd_step_call = bdd_step if type(bdd_step) is str else bdd_step.name
    found, step_func, args_dict = _find_match(bdd_step_call, testdata)
    if not found:
        Reporter.error("{}  Step Not Found".format(bdd_step_call))
        if not is_dryrun_mode:
            raise Exception("Step Implementation Not Found")
    elif is_dryrun_mode:
        Reporter.log(bdd_step_call, message_type=MessageType.TestStepPass)
    else:
        try:
            if args_dict:
                step_func(**args_dict)
            else:
                step_func()
        except Exception as e:
            Reporter.log([bdd_step_call, str(e)], message_type=MessageType.TestStepFail)


def _gen_code_snnipet(bdd_step):
    pass


def _convertPrameter(s):
    s = re.sub(r'<[a-z0-9-_]+>', r'${\g<0>}', s)
    return s.replace("${<", "${").replace(">}", "}")


def _find_match(bdd_step_call, testdata):
    from qaf.automation.core.configurations_manager import ConfigurationsManager as CM

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
