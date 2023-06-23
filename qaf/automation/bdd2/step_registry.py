from __future__ import absolute_import

import os
from functools import partial

from behave.matchers import Match, get_matcher
from behave.textutil import text as _text

# pylint: disable=undefined-all-variable
__all__ = [
    "given", "when", "then", "step", "and", "but",
    "Given", "When", "Then", "Step", "And", "But"
]

class StepRegistry:
    def __init__(self):
        self.registry = []

    def discover_package(self, package):
        pass

    def register_step(self, step):
        step_location = Match.make_location(step.func)
        step_text = _text(step.description)
        for existing in self.registry:
            if self.same_step_definition(existing.matcher, step_text, step_location):
                # -- EXACT-STEP: Same step function is already registered.
                # This may occur when a step module imports another one.
                return
        # matcher = get_matcher(step, step_text)
        step.matcher = get_matcher(step.func, step_text)
        self.registry.append(step)

    def lookup(self, step):
        step_name = step if type(step) is str else step.name
        for step_definition in self.registry:
            match = step_definition.matcher.match(step_name)
            if match:
                return step_definition, match
        return None, None

    @staticmethod
    def same_step_definition(matcher, other_pattern, other_location):
        return (matcher.pattern == other_pattern and
                matcher.location == other_location and
                other_location.filename != "<string>")


step_registry = StepRegistry()


def load_step_modules(step_paths):
    """Load step modules with step definitions from step_paths directories."""
    from behave import matchers
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


# -- Create the decorators
# pylint: disable=redefined-outer-name
def setup_step_decorators(run_context=None):
    from qaf.automation.bdd2.qaf_teststep import QAFTestStep
    if run_context is None:
        run_context = globals()
    for step_type in ("given", "when", "then", "and", "step", "but"):
        run_context[step_type.title()] = run_context[step_type] = partial(QAFTestStep, keyword=step_type.title())


def register_steps():
    from qaf.automation.core import get_bundle
    import qaf.automation.step_def as step_def_path
    from qaf.automation.keys.application_properties import ApplicationProperties as AP

    step_def_path = str(os.path.abspath(step_def_path.__file__)).replace('/__init__.py', '')

    QAF_STEPS = [step_def_path]
    load_step_modules(QAF_STEPS)
    step_provider_pkgs = get_bundle().get_string(AP.STEP_PROVIDER_PKG)
    if step_provider_pkgs:
        step_provider_pkg_list = step_provider_pkgs.replace('.', '/').split(";")
        load_step_modules(step_provider_pkg_list)


# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()
register_steps()

