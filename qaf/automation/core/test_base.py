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
import atexit
import os
import re
import time
import uuid
from builtins import dict
from time import strftime

from qaf.automation.core.checkpoint_bean import CheckPointBean
from qaf.automation.core.command_log_bean import CommandLogBean
from qaf.automation.core.configurations_manager import ConfigurationsManager
from qaf.automation.core.message_type import MessageType
from qaf.automation.keys.application_properties import ApplicationProperties as qafKeys
from qaf.automation.ui.webdriver.driver_factory import create_driver

"""
    @author: Chirag Jayswal
"""
get_bundle = ConfigurationsManager.get_bundle
prepareForShutdown = False

QAF_COMMAND_LOG_KEY = "commandLog"
QAF_CHECKPOINTS_KEY = "checkPointResults"
QAF_CONTEXT_KEY = "__qaftestbase_ctx"
QAF_DRIVER_CONTEXT_KEY = "__driver_ctx"

QAF_VERIFICATION_ERRORS_KEY = "verificationErrors"
OUTPUT_TEST_RESULTS_DIR = get_bundle().get_or_set('test.results.dir',
                                                  os.environ.get('test.results.dir', "test-results"))
REPORT_DIR = get_bundle().get_or_set('json.report.root.dir',
                                     os.environ.get('json.report.root.dir',
                                                    os.path.join(OUTPUT_TEST_RESULTS_DIR,
                                                                 strftime('%d-%m-%Y_%H_%M_%S',
                                                                          time.localtime()))))


def has_driver(name=None):
    driver_name = name or get_bundle().get_string(qafKeys.DRIVER_NAME, "firefoxDriver")
    return driver_name in _get_driver_ctx()


def get_driver(name=None):
    driver_name = name or get_bundle().get_string(qafKeys.DRIVER_NAME, "firefoxDriver")
    driver_ctx = _get_driver_ctx()
    if driver_name not in driver_ctx and not prepareForShutdown:
        driver_ctx[driver_name] = create_driver(driver_name.lower())
    if driver_name.lower() != get_bundle().get_string(qafKeys.DRIVER_NAME, "").lower():
        get_bundle().set_property(qafKeys.DRIVER_NAME, driver_name)
        # set driver/browser specific resources
        browser = re.sub(r'(?i)remote|driver', '', driver_name)
        driver_resources: str | None = get_bundle().get_string(qafKeys.DRIVER_RESOURCES_FORMAT.format(browser))
        if driver_resources is not None:
            get_bundle().load(driver_resources)
    return driver_ctx[driver_name]


def set_driver(driver_name, driver):
    _get_driver_ctx()[driver_name] = driver


def tear_down(driver_name=None):
    driver_ctx = _get_driver_ctx()
    if driver_name:
        if driver_name in driver_ctx:
            driver = driver_ctx.pop(driver_name)
            if driver:
                driver.quit()
    else:
        for k in list(driver_ctx.keys()):
            driver = driver_ctx.pop(k)
            if driver:
                driver.quit()


def _get_driver_ctx():
    return context().get(QAF_DRIVER_CONTEXT_KEY)


def context():
    ctx = ConfigurationsManager.get_bundle().get(QAF_CONTEXT_KEY, None)
    if ctx is None:
        ctx = dict()
        ctx[QAF_DRIVER_CONTEXT_KEY] = {}
        ctx[QAF_COMMAND_LOG_KEY] = []
        ctx[QAF_CHECKPOINTS_KEY] = []
        ctx[QAF_VERIFICATION_ERRORS_KEY] = 0
        ConfigurationsManager.get_bundle().set_property(QAF_CONTEXT_KEY, ctx)
    return ctx


def clear_assertions_log():
    get_checkpoint_results().clear()
    clear_verification_errors()
    get_command_logs().clear()
    if "_current_step" in context():
        context().pop("_current_step")
    if "last_captured_screenshot" in context():
        context().pop("last_captured_screenshot")


def clear_verification_errors():
    context()[QAF_VERIFICATION_ERRORS_KEY] = 0


def get_checkpoint_results():
    return context()[QAF_CHECKPOINTS_KEY]


def get_command_logs():
    return context()[QAF_COMMAND_LOG_KEY]


def get_verification_errors() -> int:
    return int(context()[QAF_VERIFICATION_ERRORS_KEY])


def is_verification_failed() -> bool:
    return get_verification_errors() > 0


def start_step(step_name, display_name, args=[]):
    current_step = _get_cur_step()
    step = _StepLogger(step_name, display_name, current_step, args)


def end_step(status: bool, result=None):
    current_step = _get_cur_step()
    success = current_step.checkpoint.is_success()
    current_step.set_status(False if not success else status, result)
    if "last_captured_screenshot" in context():
        last_captured_screenshot = context().pop("last_captured_screenshot")
        current_step.checkpoint.screenshot = last_captured_screenshot
    _set_cur_step(current_step.get_parent())
    # del current_step


def add_command(log: CommandLogBean) -> None:
    _get_cur_step().add_log(log)


def add_checkpoint(checkpoint: CheckPointBean) -> None:
    if not checkpoint.is_success():
        verification_errors = get_verification_errors() + 1
        context()[QAF_VERIFICATION_ERRORS_KEY] = verification_errors
        if not checkpoint.screenshot:
            checkpoint.screenshot = take_screenshot()
    _get_cur_step().add_checkpoint(checkpoint)


def _get_cur_step():
    if "_current_step" in context():
        return context()["_current_step"]
    else:
        return _StepLogger("","", None)


def _set_cur_step(step):
    context()["_current_step"] = step


def take_screenshot() -> str:
    if has_driver():
        try:
            os.makedirs(name=os.path.join(REPORT_DIR, 'img'), exist_ok=True)
            filename = os.path.join(REPORT_DIR, 'img', str(uuid.uuid4()) + '.png')
            get_driver().save_screenshot(filename=filename)
            context()["last_captured_screenshot"] = filename
            return filename
        except Exception:
            return filename
    return ""


def shut_down():
    global prepareForShutdown
    prepareForShutdown = True
    print("Preparing For Shut Down...")
    tear_down()
    #ResultUpdator.awaitTermination()


atexit.register(shut_down)


class _StepLogger(object):

    def __init__(self, name, dispay_name, parent, args=[]):
        self.st_time = round(time.time() * 1000)
        checkpoint = CheckPointBean()
        command_log = CommandLogBean()
        self.checkpoint = checkpoint
        self.command_log = command_log
        if not name or not parent:
            self.checkpoint.subCheckPoints = get_checkpoint_results()
            self.command_log.subLogs = get_command_logs()
            self.parent = self
        else:
            try:
                self.parent = parent
                context()["_current_step"] = self
                checkpoint.message = dispay_name
                command_log.commandName = name
                command_log.args = args
                self.parent.add_log(command_log)
                self.parent.add_checkpoint(checkpoint)
            except Exception as e:
                print("Error in init _StepLogger...")
                print(e)

    def add_log(self, log: CommandLogBean) -> None:
        self.command_log.subLogs.append(log)

    def add_checkpoint(self, checkpoint: CheckPointBean) -> None:
        self.checkpoint.subCheckPoints.append(checkpoint)

    def get_parent(self):
        return self.parent

    def set_status(self, success: bool, result=None):
        duration = round(time.time() * 1000) - self.st_time
        self.checkpoint.duration = duration
        self.command_log.duration = duration
        if success is None:
            self.checkpoint.type = MessageType.TestStep
            self.command_log.result = "Unknown"
        else:
            self.checkpoint.type = MessageType.TestStepPass if success else MessageType.TestStepFail
            self.command_log.result = "success" if success else "failed"

        if result is not None:
            self.command_log.result = result

