from pluggy import PluginManager, HookspecMarker, HookimplMarker

__all__ = [
    "qafhook"
]
_QAF_LISTENER = "QAFListener"
pluginmagager = PluginManager(_QAF_LISTENER)
qafhookspec = HookspecMarker(_QAF_LISTENER)
qafhook = HookimplMarker(_QAF_LISTENER)


class QAFWebDriverListener:
    from qaf.automation.ui.webdriver.command_tracker import CommandTracker
    from qaf.automation.ui.webdriver.qaf_web_driver import QAFWebDriver

    @qafhookspec
    def before_driver_initialize(self, capabilities):
        """ driver initialization """

    @qafhookspec
    def on_driver_initialize(self, driver: QAFWebDriver):
        """ driver initialization """

    @qafhookspec
    def on_driver_initialization_failure(self, capabilities, e):
        """ driver initialization """

    @qafhookspec
    def before_driver_command(self, driver: QAFWebDriver, command_tracker: CommandTracker):
        """driver command"""

    @qafhookspec
    def after_driver_command(self, driver: QAFWebDriver, command_tracker: CommandTracker):
        """driver command"""

    @qafhookspec
    def on_driver_command_failure(self, driver: QAFWebDriver, command_tracker: CommandTracker):
        """driver command"""


class QAFElementListener:
    from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement
    from qaf.automation.ui.webdriver.command_tracker import CommandTracker

    @qafhookspec
    def before_element_command(self, element: QAFWebElement, command_tracker: CommandTracker):
        """ element command """

    @qafhookspec
    def after_element_command(self, element: QAFWebElement, command_tracker: CommandTracker):
        """ element command """

    @qafhookspec
    def on_element_command_failure(self, element: QAFWebElement, command_tracker: CommandTracker):
        """ element command """


class StepListener:
    from qaf.automation.bdd2.qaf_teststep import StepTracker

    @qafhookspec
    def before_step(self, step_tracker: StepTracker):
        """ step """

    @qafhookspec
    def after_step(self, step_tracker: StepTracker):
        """ step """


# pluginmagager.register(self, qaf_teststep)
