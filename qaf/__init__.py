__version__ = "1.2.1"

from qaf.automation.core.qaf_exceptions import KeyNotFoundError

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.core.resources_manager import ResourcesManager


ResourcesManager().set_up()

if not CM().contains_key(key=AP.TESTING_APPROACH):
    raise KeyNotFoundError(message=AP.TESTING_APPROACH + ' e.g. behave, pytest')

if CM().get_str_for_key(key=AP.TESTING_APPROACH).lower() == 'behave':
    from behave.runner_util import load_step_modules
    import os

    import qaf.automation.step_def as step_def_path
    step_def_path = str(os.path.abspath(step_def_path.__file__)).replace('/__init__.py', '')

    SUBSTEP_DIRS = [step_def_path]
    load_step_modules(SUBSTEP_DIRS)
