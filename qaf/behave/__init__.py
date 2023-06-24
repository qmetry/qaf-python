import os

from qaf.automation.core import get_bundle
from qaf.automation.keys.application_properties import ApplicationProperties
from qaf.behave.qaf_behave_plugin import (before_scenario, after_scenario, before_step, after_step)


def setup_qaf():
    get_bundle().set_property(ApplicationProperties.TESTING_APPROACH, "behave")

    from behave.runner_util import load_step_modules
    import qaf.automation.step_def as step_def_path
    step_def_path = str(os.path.abspath(step_def_path.__file__)).replace('/__init__.py', '')

    QAF_STEPS = [step_def_path]
    load_step_modules(QAF_STEPS)
    step_provider_pkgs = get_bundle().get_string(ApplicationProperties.STEP_PROVIDER_PKG)
    if step_provider_pkgs:
        step_provider_pkg_list = step_provider_pkgs.replace('.', '/').split(";")
        load_step_modules(step_provider_pkg_list)
