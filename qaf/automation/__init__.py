#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.qaf_exceptions import KeyNotFoundError
from qaf.automation.keys.application_properties import ApplicationProperties as AP


if CM.get_bundle().get_string(key=AP.TESTING_APPROACH,default="behave").lower() == 'behave':
    from behave.runner_util import load_step_modules
    import os

    import qaf.automation.step_def as step_def_path
    step_def_path = str(os.path.abspath(step_def_path.__file__)).replace('/__init__.py', '')

    SUBSTEP_DIRS = [step_def_path]
    load_step_modules(SUBSTEP_DIRS)