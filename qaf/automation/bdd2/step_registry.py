from __future__ import absolute_import

from functools import partial

from behave.matchers import Match, get_matcher
from behave.textutil import text as _text

# pylint: disable=undefined-all-variable
__all__ = [
    "given", "when", "then", "step", "and",
    "Given", "When", "Then", "Step", "And"
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
        #matcher = get_matcher(step, step_text)
        step.matcher=get_matcher(step.func, step_text)
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


# -- Create the decorators
# pylint: disable=redefined-outer-name
def setup_step_decorators(run_context=None):
    from qaf.automation.bdd2.qaf_teststep import QAFTestStep
    if run_context is None:
        run_context = globals()
    for step_type in ("given", "when", "then", "and", "step"):
        run_context[step_type.title()] = run_context[step_type] = partial(QAFTestStep,keyword=step_type.title())


# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()


