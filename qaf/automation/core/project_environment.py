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

import os

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.resources_manager import ResourcesManager
from qaf.automation.keys.application_properties import ApplicationProperties as AP


class ProjectEnvironment:
    """
    This class will set up application properties, locators, etc.
    """

    @staticmethod
    def set_up() -> None:
        """
        This method will initialise the application properties and locators storage file.

        Returns:
            None
        """
        ResourcesManager().set_up()
        ProjectEnvironment.set_executable_path()

    @staticmethod
    def set_executable_path():
        executable_path = CM().get_str_for_key(AP.EXECUTABLE_PATH,"")
        all_executable_path = executable_path.split(";")
        for each_executable_path in all_executable_path:
            os.environ["PATH"] += os.pathsep + each_executable_path
