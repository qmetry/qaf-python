from abc import ABC, abstractmethod

from qaf.automation.ui.webdriver.command_tracker import CommandTracker


class DriverListener(ABC):
    @abstractmethod
    def before_command(self, driver, command_tracker: CommandTracker):
        pass

    @abstractmethod
    def after_command(self, driver, command_tracker: CommandTracker):
        pass

    @abstractmethod
    def on_exception(self, driver, command_tracker: CommandTracker):
        pass


class ElementListener(ABC):
    @abstractmethod
    def before_command(self, element, command_tracker: CommandTracker):
        pass

    @abstractmethod
    def after_command(self, element, command_tracker: CommandTracker):
        pass

    @abstractmethod
    def on_exception(self, element, command_tracker: CommandTracker):
        pass