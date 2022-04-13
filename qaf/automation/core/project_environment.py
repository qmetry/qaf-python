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
        executable_path = CM().get_str_for_key(AP.EXECUTABLE_PATH)
        all_executable_path = executable_path.split(";")
        for each_executable_path in all_executable_path:
            os.environ["PATH"] += os.pathsep + each_executable_path
